import io
from typing import BinaryIO, Dict, Optional, Tuple

import multipart


def get_body_from_form_data(
    body: bytes, boundary: str
) -> Tuple[Optional[bytes], Dict[str, str]]:
    body_stream = io.BytesIO(body)
    parser = multipart.MultipartParser(body_stream, boundary=boundary)

    data = None
    headers: Dict[str, str] = {}
    for prt in parser.parts():
        if prt.name == "upload_file":
            headers["key"] = prt.name
            data = prt.file.read()
        else:
            val = prt.file.read()
            if prt.name == "file":
                data = val
            else:
                headers[prt.name] = val.decode("utf-8")
    return data, headers


def read_chunked_body(reader: BinaryIO) -> bytes:
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
            break
    return chunked_body


def chunk_body(body: bytes) -> bytes:
    chunked = b""
    chunked += f"{len(body):x}".encode("utf-8")
    chunked += b"\r\n"
    chunked += body
    chunked += b"\r\n"
    chunked += b"0"
    return chunked
