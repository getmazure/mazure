import re
from gzip import compress

from mazure.mazure_core import ResponseType
from mazure.mazure_core.mazure_request import MazureRequest

from .route_mapping import registered_services  # pylint: disable

ERROR_NOT_YET_IMPLEMENTED = "Not  yet implemented".encode("utf-8")


def execute(request: MazureRequest) -> ResponseType:
    status_code, res_headers, res_body = _get_response(request)

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


def _get_response(request: MazureRequest) -> ResponseType:
    if request.method in registered_services:
        for path, func in registered_services[request.method].items():
            requested_path = request.host + request.path
            if re.match(path, requested_path):
                return func(request)

    return 404, {}, ERROR_NOT_YET_IMPLEMENTED
