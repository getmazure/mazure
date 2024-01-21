import os
from unittest import SkipTest
from uuid import uuid4

import pytest
import requests


@pytest.fixture
def skip_if_proxy_not_configured() -> None:  # type: ignore[misc]
    if "HTTPS_PROXY" not in os.environ:
        raise SkipTest("Can't test this without a proxy configured")
    yield
