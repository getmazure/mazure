from datetime import datetime

from mazure.mazure_core import ResponseType
from mazure.mazure_core.mazure_request import MazureRequest
from mazure.mazure_core.route_mapping import register, register_parent

from .models.blob import Blob
from .models.storage_container import StorageContainer


@register_parent(path="https://[-_a-z0-9A-Z]+.blob.core.windows.net")
class StorageHost:
    pass


@register(
    parent=StorageHost,
    path=r"/$",
    method="GET",
)
def list_containers(request: MazureRequest) -> ResponseType:
    resp = f'<?xml version="1.0" encoding="utf-8"?><EnumerationResults ServiceEndpoint="{request.host}/"><MaxResults>5000</MaxResults><Containers>'
    for container in StorageContainer.select():
        resp += container.to_xml()
    resp += "</Containers><NextMarker /></EnumerationResults>"
    return 200, {}, resp.encode("utf-8")


@register(
    parent=StorageHost,
    path=r"/[-_a-z0-9A-Z]+$",
    method="PUT",
)
def create_container(request: MazureRequest) -> ResponseType:
    # ?restype=container
    name = request.parsed_path.path[1:]  # skip the initial /
    container = StorageContainer.get_or_none(StorageContainer.name == name)
    if container is not None:
        time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S:%sZ")
        resp = f"""<?xml version="1.0" encoding="utf-8"?><Error><Code>ContainerAlreadyExists</Code><Message>The specified container already exists.
    RequestId:3d98fb17-201e-0064-229a-4c434a000000
    Time:{time}</Message></Error>"""
        return 409, {"x-ms-error-code": "ContainerAlreadyExists"}, resp.encode("utf-8")

    StorageContainer.create(name=name)
    # headers
    # Content-Length: 0
    # Last-Modified: Sun, 21 Jan 2024 18:50:43 GMT
    # ETag: "0x8DC1AB1DEF3444F
    return 201, {}, b""


@register(
    parent=StorageHost,
    path=r"/[-_a-z0-9A-Z]+$",
    method="DELETE",
)
def delete_container(request: MazureRequest) -> ResponseType:
    # ?restype=container
    if StorageContainer.delete_by_id(request.parsed_path.path.split("/")[-1]):
        return 202, {}, b""
    error = b'<?xml version="1.0" encoding="utf-8"?><Error><Code>ContainerNotFound</Code><Message>The specified container does not exist.\nRequestId:a317f225-701e-008d-4a65-4d8500000000\nTime:2024-01-22T18:58:46.0910462Z</Message></Error>'
    return 404, {"Content-Type": "application/xml"}, error


@register(
    parent=StorageHost,
    path=r"/[-_a-z0-9A-Z]+$",
    method="GET",
)
def list_blobs(request: MazureRequest) -> ResponseType:
    # ?restype=container
    resp = f'<?xml version="1.0" encoding="utf-8"?><EnumerationResults ServiceEndpoint="https://{request.host}/" ContainerName="{request.parsed_path.path[1:]}"><MaxResults>5000</MaxResults><Blobs>'
    for blob in Blob.select():
        resp += blob.to_xml()
    resp += "</Blobs><NextMarker /></EnumerationResults>"
    return 200, {"Content-Type": "application/xml"}, resp.encode("utf-8")


@register(
    parent=StorageHost,
    path=r"/[-_a-z0-9A-Z]+/[-_a-z0-9A-Z]+",
    method="PUT",
)
def upload_blob(request: MazureRequest) -> ResponseType:
    # storage_container = request.parsed_path.path.split("/")[1]
    blob_name = "/".join(request.parsed_path.path.split("/")[2:])
    content_type = request.headers.get("x-ms-blob-content-type")
    Blob.create(name=blob_name, content=request.body, content_type=content_type)
    headers = {
        "Content-Length": "0",
        "Content-MD5": "",
        "ETag": "",
        "x-ms-content-crc64": "",
    }
    return 201, headers, b""


@register(
    parent=StorageHost,
    path=r"/[-_a-z0-9A-Z]+/[-_a-z0-9A-Z.]+$",
    method="GET",
)
def download_blob(request: MazureRequest) -> ResponseType:
    # storage_container = request.parsed_path.path.split("/")[1]
    blob_name = "/".join(request.parsed_path.path.split("/")[2:])
    blob = Blob.get_by_id(blob_name)
    content_length = str(len(blob.content))
    headers = {
        "Content-Length": content_length,
        "Content-Type": blob.content_type,
        "Content-Range": f"bytes 0-{content_length}/{content_length}",
        "ETag": "",
        "x-ms-creation-time": "",
        "x-ms-blob-content-md5": "",
        "x-ms-lease-status": "unlocked",
        "x-ms-lease-state": "available",
        "x-ms-blob-type": "BlockBlob",
        "x-ms-server-encrypted": "true",
    }
    return 200, headers, blob.content
