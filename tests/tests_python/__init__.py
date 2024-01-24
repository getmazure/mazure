import re
from typing import Generator
from urllib.parse import ParseResult, urlparse

import pytest
import requests
import responses


@pytest.fixture(autouse=True)
def load_responses() -> Generator[None, None, None]:
    from mazure import azure_services  # pylint: disable=C0415,W0611
    from mazure.mazure_core import ResponseType  # pylint: disable=C0415
    from mazure.mazure_core.mazure_request import MazureRequest  # pylint: disable=C0415
    from mazure.mazure_core.route_mapping import (  # pylint: disable=C0415
        registered_parents,
        registered_services,
    )

    r_mock = responses.RequestsMock(assert_all_requests_are_fired=False)
    r_mock.start()

    def request_callback(request: requests.PreparedRequest) -> ResponseType:
        parsed: ParseResult = urlparse(request.url)  # type: ignore[assignment]
        mazure_request = MazureRequest(
            method=request.method,  # type: ignore
            host=parsed.hostname,  # type: ignore
            path=parsed.path,
            headers=request.headers,  # type: ignore
            body=request.body,  # type: ignore
            parsed_path=parsed,
        )
        for method, fn_per_path in registered_services.items():
            if method != request.method:
                continue
            for path, func in fn_per_path.items():
                requested_path = parsed.scheme + "://" + parsed.netloc + parsed.path
                if re.compile(path).match(requested_path):
                    return func(mazure_request)

        raise ValueError

    for _, url in registered_parents.items():
        for method in ["GET", "DELETE", "POST", "PUT", "PATCH", "HEAD"]:
            r_mock.add_callback(
                method=method,
                url=re.compile(url),
                callback=request_callback,
                match_querystring=False,
            )

    yield

    r_mock.stop()
