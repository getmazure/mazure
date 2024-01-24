import requests
import xmltodict
from peewee import SqliteDatabase

from mazure.azure_services.management.graph.models.application import (
    Application,
    DeletedApplication,
)
from mazure.azure_services.management.storage.models.async_operation import (
    AsyncStorageOperation,
)
from mazure.azure_services.management.storage.models.storage_account import (
    StorageAccount,
    StorageAccountKey,
    StorageAccountKeyLink,
)
from mazure.azure_services.storage.models.blob import Blob
from mazure.azure_services.storage.models.storage_container import StorageContainer

# Fixtures are applied automatically, but we do have to load them
from ... import load_responses  # pylint: disable=W0611

MODELS = [
    AsyncStorageOperation,
    Application,
    Blob,
    DeletedApplication,
    StorageAccount,
    StorageAccountKey,
    StorageAccountKeyLink,
    StorageContainer,
]

# use an in-memory SQLite for tests.
_test_db = SqliteDatabase(":memory:")


class TestStorageAccounts:
    def setup_method(self) -> None:
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        _test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        _test_db.connect()
        _test_db.create_tables(MODELS)

        # create group

    def teardown_method(self) -> None:
        _test_db.drop_tables(MODELS)

        # Close connection to db.
        _test_db.close()

    def test_create_container(self) -> None:
        # Create StorageAccount
        storage_accnt_name = "storage_account"
        requests.put(
            f"https://management.azure.com/subscriptions/s/resourceGroups/r/providers/Microsoft.Storage/storageAccounts/{storage_accnt_name}",
            timeout=2,
            json={
                "kind": "StorageV2",
                "location": "francecentral",
                "sku": {"name": "Standard_ZRS"},
            },
        )

        # List Containers
        resp = requests.get(
            f"https://{storage_accnt_name}.blob.core.windows.net", timeout=2
        )
        assert resp.status_code == 200
        body = xmltodict.parse(resp.content)
        assert body["EnumerationResults"]["Containers"] is None

        # Create Container
        container_name = "mycontainer"
        resp = requests.put(
            f"https://{storage_accnt_name}.blob.core.windows.net/{container_name}",
            timeout=2,
        )
        assert resp.status_code == 201
        assert resp.content == b""

        # Create Container again
        resp = requests.put(
            f"https://{storage_accnt_name}.blob.core.windows.net/{container_name}",
            timeout=2,
        )
        assert resp.status_code == 409
        assert b"The specified container already exists." in resp.content

        # List Containers
        resp = requests.get(
            f"https://{storage_accnt_name}.blob.core.windows.net", timeout=2
        )
        assert resp.status_code == 200
        body = xmltodict.parse(resp.content)
        assert len(body["EnumerationResults"]["Containers"]) == 1

        # Delete Container
        resp = requests.delete(
            f"https://{storage_accnt_name}.blob.core.windows.net/{container_name}?restype=container",
            timeout=2,
        )
        assert resp.status_code == 202
        assert resp.content == b""

        # List Containers
        resp = requests.get(
            f"https://{storage_accnt_name}.blob.core.windows.net", timeout=2
        )
        assert resp.status_code == 200
        body = xmltodict.parse(resp.content)
        assert body["EnumerationResults"]["Containers"] is None

        # Delete Container again
        resp = requests.delete(
            f"https://{storage_accnt_name}.blob.core.windows.net/{container_name}?restype=container",
            timeout=2,
        )
        assert resp.status_code == 404
        assert resp.headers.get("Content-Type") == "application/xml"
        assert b"ContainerNotFound" in resp.content

    def test_upload_blob(self) -> None:
        # Create StorageAccount
        storage_accnt_name = "storage_account"
        requests.put(
            f"https://management.azure.com/subscriptions/s/resourceGroups/r/providers/Microsoft.Storage/storageAccounts/{storage_accnt_name}",
            timeout=2,
            json={
                "kind": "StorageV2",
                "location": "francecentral",
                "sku": {"name": "Standard_ZRS"},
            },
        )

        # Create Container
        container_name = "mycontainer"
        requests.put(
            f"https://{storage_accnt_name}.blob.core.windows.net/{container_name}",
            timeout=2,
        )

        # List Blobs
        resp = requests.get(
            f"https://{storage_accnt_name}.blob.core.windows.net/{container_name}",
            timeout=2,
        )
        assert resp.status_code == 200
        body = xmltodict.parse(resp.content)
        assert body["EnumerationResults"]["Blobs"] is None

        # Upload file
        data = "some 😁 bytes".encode("utf-8")
        resp = requests.put(
            f"https://{storage_accnt_name}.blob.core.windows.net/{container_name}/myfile.txt",
            timeout=2,
            data=data,
            headers={"x-ms-blob-content-type": "text/markdown"},
        )
        assert resp.status_code == 201
        assert "Content-MD5" in resp.headers

        # Download file
        resp = requests.get(
            f"https://{storage_accnt_name}.blob.core.windows.net/{container_name}/myfile.txt",
            timeout=2,
        )
        assert resp.status_code == 200
        assert resp.content == data
        assert resp.headers["Content-Type"] == "text/markdown"

        # List Blobs
        resp = requests.get(
            f"https://{storage_accnt_name}.blob.core.windows.net/{container_name}",
            timeout=2,
        )
        assert resp.status_code == 200
        body = xmltodict.parse(resp.content)
        assert len(body["EnumerationResults"]["Blobs"]) == 1
        assert body["EnumerationResults"]["Blobs"]["Blob"]["Name"] == "myfile.txt"
