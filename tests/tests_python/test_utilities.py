import io

import pytest

from mazure.mazure_proxy.utils import chunk_body, read_chunked_body


@pytest.mark.parametrize(
    "data", [b"", b"little", b"loads of data" * 3, b"gigantic data" * 42]
)
def test_chunked_body(data: bytes) -> None:
    chunked = chunk_body(data)

    roundtripped = read_chunked_body(io.BytesIO(chunked))
    assert roundtripped == data
