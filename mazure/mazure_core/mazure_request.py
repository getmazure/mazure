from email.message import Message
from typing import Any, Dict
from urllib.parse import ParseResult
from uuid import uuid4


class MazureRequest:
    def __init__(  # pylint: disable=too-many-arguments
        self,
        host: str,
        path: str,
        method: str,
        headers: Message,
        body: bytes,
        parsed_path: ParseResult,
    ):
        self.request_id = str(uuid4())
        self.default_headers: Dict[str, Any] = {
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

        self.headers = headers
        self.body = body
        self.host = host
        self.path = path
        self.method = method
        self.parsed_path = parsed_path
