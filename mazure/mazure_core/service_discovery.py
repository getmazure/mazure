import re
from gzip import compress
from typing import Any, Dict

from mazure.mazure_core import MazureRequest, ResponseType

from .route_mapping import registered_services  # pylint: disable

ERROR_NOT_YET_IMPLEMENTED = "Not  yet implemented".encode("utf-8")


def execute(request: MazureRequest) -> ResponseType:
    status_code: int
    res_headers: Dict[str, Any]
    res_body: bytes

    if request.method in registered_services:
        if request.host in registered_services[request.method]:
            operations_for_host = registered_services[request.method][request.host]

            status_code, res_headers, res_body = 404, {}, ERROR_NOT_YET_IMPLEMENTED

            for path, func in operations_for_host.items():
                if re.match(path, request.path):
                    status_code, res_headers, res_body = func(request)

        else:
            status_code, res_headers, res_body = 404, {}, ERROR_NOT_YET_IMPLEMENTED
    else:
        status_code, res_headers, res_body = 404, {}, ERROR_NOT_YET_IMPLEMENTED

    full_res_headers = request.default_headers.copy()
    full_res_headers.update(res_headers)

    if (
        "content-length" not in full_res_headers
        and full_res_headers.get("Transfer-Encoding") != "chunked"
        and "gzip"
        in [
            enc.strip() for enc in request.headers.get("Accept-Encoding", "").split(",")
        ]
    ):
        res_body = compress(res_body)
        full_res_headers["Content-Encoding"] = "gzip"

    if (
        "content-length" not in full_res_headers
        and full_res_headers.get("Transfer-Encoding") != "chunked"
        and res_body
    ):
        full_res_headers["Content-Length"] = str(len(res_body))

    return status_code, full_res_headers, res_body
