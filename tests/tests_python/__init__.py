import re
from typing import Generator
from urllib.parse import ParseResult, urlparse

import pytest
import requests
import responses


@pytest.fixture(autouse=True)
def load_responses() -> Generator[None, None, None]:
    from mazure import (  # pylint: disable=import-outside-toplevel,unused-import
        azure_services,
    )
    from mazure.mazure_core import (  # pylint: disable=import-outside-toplevel
        ResponseType,
    )
    from mazure.mazure_core.mazure_request import (  # pylint: disable=import-outside-toplevel
        MazureRequest,
    )
    from mazure.mazure_core.route_mapping import (  # pylint: disable=import-outside-toplevel
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
        for method, host_per_method in registered_services.items():
            if method != request.method:
                continue
            for host, functions_by_path in host_per_method.items():
                requested_host = parsed.scheme + "://" + parsed.netloc
                if not re.compile(host).match(requested_host):
                    continue
                for path, func in functions_by_path.items():
                    if path.match(parsed.path):
                        return func(mazure_request)
        raise ValueError

    for method, per_host in registered_services.items():
        for host in per_host.keys():
            r_mock.add_callback(
                method=method,
                url=re.compile(host),
                callback=request_callback,
                match_querystring=False,
            )

    yield

    r_mock.stop()
