from mazure.azure_services.management.response import ManagementResponse
from mazure.mazure_core import ResponseType


def get(host: str, path: str, method: str, body: bytes) -> ResponseType:
    if host == "https://management.azure.com":
        return ManagementResponse().process_request(path, method, body=body)

    return 404, {}, f"Service behind {host} not  yet implemented".encode("utf-8")
