# -*- coding: utf-8 -*-
import ssl
from http.server import BaseHTTPRequestHandler
from subprocess import CalledProcessError, check_output
from typing import Any, Dict
from urllib.parse import urlparse

from mazure import azure_services  # pylint: disable=unused-import
from mazure.mazure_core import MazureRequest
from mazure.mazure_core.service_discovery import execute

from . import debug, info
from .certificate_creator import CertificateCreator
from .utils import get_body_from_form_data, read_chunked_body

# Adapted from https://github.com/xxlv/proxy3


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
        debug(f"{self.command} {host}{path}")

        parsed = urlparse(path)
        request = MazureRequest(
            host=host,
            path=parsed.path,
            method=req.command,
            headers=req.headers,
            body=req_body,
        )
        res_status, res_headers, res_body = execute(request)

        res_reason = "OK"

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
            req_body = read_chunked_body(self.rfile)
        return req_body

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
