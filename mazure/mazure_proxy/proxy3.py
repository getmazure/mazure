# -*- coding: utf-8 -*-
import ssl
from gzip import compress
from http.server import BaseHTTPRequestHandler
from subprocess import CalledProcessError, check_output
from typing import Any, Dict
from uuid import uuid4

from mazure.mazure_core.service_discovery import get

from . import debug, info
from .certificate_creator import CertificateCreator
from .utils import get_body_from_form_data

# Adapted from https://github.com/xxlv/proxy3


class MazureRequest:
    def __init__(self) -> None:
        self.request_id = str(uuid4())
        self.default_headers = {
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Content-Type": "application/json; charset=utf-8",
            "Expires": "-1",
            "Vary": "Accept-Encoding",
            "x-ms-ratelimit-remaining-subscription-reads": 11999,
            "x-ms-request-id": self.request_id,
            "x-ms-correlation-request-id": self.request_id,
            "x-ms-routing-request-id": f"FRANCESOUTH:20240108T215501Z:{self.request_id}",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "X-Content-Type-Options": "nosniff",
            "Date": "Mon, 08 Jan 2024 21:55:01 GMT",
        }

    def parse_request(  # pylint: disable=too-many-arguments
        self,
        method: str,
        host: str,
        path: str,
        headers: Any,
        body: bytes,
        form_data: Dict[str, Any],  # pylint: disable=unused-argument
    ) -> Any:
        status_code, res_headers, res_body = get(host, path, method, body=body)

        full_res_headers = self.default_headers.copy()
        full_res_headers.update(res_headers)

        if "content-length" not in full_res_headers and "gzip" in [
            enc.strip() for enc in headers.get("Accept-Encoding", "").split(",")
        ]:
            res_body = compress(res_body)
            full_res_headers["Content-Encoding"] = "gzip"

        if "content-length" not in full_res_headers and res_body:
            full_res_headers["Content-Length"] = str(len(res_body))

        return status_code, full_res_headers, res_body


class ProxyRequestHandler(BaseHTTPRequestHandler):
    timeout = 5

    def __init__(self, *args: Any, **kwargs: Any):
        self.protocol_version = "HTTP/1.1"
        self.cert_creator = CertificateCreator()
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    @staticmethod
    def validate() -> None:
        debug("Starting initial validation...")
        CertificateCreator().validate()
        # Validate the openssl command is available
        try:
            debug("Verifying SSL version...")
            svn_output = check_output(["openssl", "version"])
            debug(svn_output)
        except CalledProcessError as e:
            info(e.output)
            raise

    def process_connect(self) -> None:
        certpath = self.cert_creator.create(self.path)

        self.wfile.write(
            f"{self.protocol_version} 200 Connection Established\r\n".encode("utf-8")
        )
        self.send_header("k", "v")
        self.end_headers()

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(
            keyfile=CertificateCreator.certkey,
            certfile=certpath,
        )
        ssl_context.check_hostname = False
        self.connection = (  # pylint: disable=attribute-defined-outside-init
            ssl_context.wrap_socket(self.connection, server_side=True)
        )
        self.rfile = self.connection.makefile("rb", self.rbufsize)  # type: ignore  # pylint: disable=attribute-defined-outside-init
        self.wfile = self.connection.makefile("wb", self.wbufsize)  # type: ignore  # pylint: disable=attribute-defined-outside-init

        conntype = self.headers.get("Proxy-Connection", "")
        if self.protocol_version == "HTTP/1.1" and conntype.lower() != "close":
            self.close_connection = 0  # type: ignore  # pylint: disable=attribute-defined-outside-init
        else:
            self.close_connection = 1  # type: ignore  # pylint: disable=attribute-defined-outside-init

    def process_get(self) -> None:
        req = self
        req_body = self._read_body(req)
        if self.headers.get("Content-Type", "").startswith("multipart/form-data"):
            boundary = self.headers["Content-Type"].split("boundary=")[-1]
            req_body, form_data = get_body_from_form_data(req_body, boundary)  # type: ignore
            for key, val in form_data.items():
                self.headers[key] = [val]
        else:
            form_data = {}

        req_body = self.decode_request_body(req.headers, req_body)  # type: ignore
        if isinstance(self.connection, ssl.SSLSocket):
            host = "https://" + req.headers["Host"]
        else:
            host = "http://" + req.headers["Host"]
        path = req.path
        debug(f"{self.command} {host} {path}")

        response = MazureRequest().parse_request(
            method=req.command,
            host=host,
            path=path,
            headers=req.headers,
            body=req_body,
            form_data=form_data,
        )
        res_status, res_headers, res_body = response

        res_reason = "OK"
        if isinstance(res_body, str):
            res_body = res_body.encode("utf-8")

        self.wfile.write(
            f"{self.protocol_version} {res_status} {res_reason}\r\n".encode("utf-8")
        )
        if res_headers:
            for k, v in res_headers.items():
                if isinstance(v, bytes):
                    self.send_header(k, v.decode("utf-8"))
                else:
                    self.send_header(k, v)
            self.end_headers()
        if res_body:
            self.wfile.write(res_body)
        self.close_connection = True  # pylint: disable=attribute-defined-outside-init

    def _read_body(self, req: BaseHTTPRequestHandler) -> bytes:
        req_body = b""
        if "Content-Length" in req.headers:
            content_length = int(req.headers["Content-Length"])
            req_body = self.rfile.read(content_length)
        elif "chunked" in self.headers.get("Transfer-Encoding", ""):
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding
            req_body = self.read_chunked_body(self.rfile)
        return req_body

    def read_chunked_body(self, reader: Any) -> bytes:
        chunked_body = b""
        while True:
            line = reader.readline().strip()
            chunk_length = int(line, 16)
            if chunk_length != 0:
                chunked_body += reader.read(chunk_length)

            # Each chunk is followed by an additional empty newline
            reader.readline()

            # a chunk size of 0 is an end indication
            if chunk_length == 0:
                # AWS does send additional (checksum-)headers, but we can ignore them
                break
        return chunked_body

    def decode_request_body(self, headers: Dict[str, str], body: Any) -> Any:
        if body is None:
            return body
        if headers.get("Content-Type", "") in [
            "application/x-amz-json-1.1",
            "application/x-www-form-urlencoded; charset=utf-8",
        ]:
            return body.decode("utf-8")
        return body

    do_CONNECT = process_connect
    do_GET = process_get
    do_HEAD = process_get
    do_POST = process_get
    do_PUT = process_get
    do_PATCH = process_get
    do_DELETE = process_get
    do_OPTIONS = process_get
