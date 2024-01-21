import requests
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

# Fixtures are applied automatically, but we do have to load them
from ... import load_responses  # pylint: disable=W0611

MODELS = [
    AsyncStorageOperation,
    Application,
    DeletedApplication,
    StorageAccount,
    StorageAccountKey,
    StorageAccountKeyLink,
]

# use an in-memory SQLite for tests.
test_db = SqliteDatabase(":memory:")


class TestStorageAccounts:
    def setup(self) -> None:
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        test_db.connect()
        test_db.create_tables(MODELS)

        # create group

    def teardown(self) -> None:
        test_db.drop_tables(MODELS)

        # Close connection to db.
        test_db.close()

    def test_name_exists(self) -> None:
        storage_container_name = "storage_container"
        req_body = {
            "name": storage_container_name,
            "type": "Microsoft.Storage/storageAccounts",
        }

        resp = requests.post(
            "https://management.azure.com/subscriptions/s/providers/Microsoft.Storage/checkNameAvailability",
            json=req_body,
            timeout=2,
        )
        assert resp.status_code == 200
        assert resp.json() == {"nameAvailable": True}

        requests.put(
            f"https://management.azure.com/subscriptions/s/resourceGroups/r/providers/Microsoft.Storage/storageAccounts/{storage_container_name}",
            timeout=2,
            json={
                "kind": "StorageV2",
                "location": "francecentral",
                "properties": {
                    "encryption": {
                        "keySource": "Microsoft.Storage",
                        "services": {"blob": {"enabled": True}},
                    }
                },
                "sku": {"name": "Standard_ZRS"},
            },
        )

        resp = requests.post(
            "https://management.azure.com/subscriptions/s/providers/Microsoft.Storage/checkNameAvailability",
            json=req_body,
            timeout=2,
        )
        assert resp.status_code == 200
        assert resp.json() == {
            "message": f"The storage account named {storage_container_name} is already taken.",
            "nameAvailable": False,
            "reason": "AlreadyExists",
        }

    def test_create_account(self) -> None:
        # list returns nothing
        resp = requests.get(
            "https://management.azure.com/subscriptions/s/providers/Microsoft.Storage/storageAccounts",
            timeout=2,
        )
        assert resp.status_code == 200
        assert resp.json() == {"value": []}

        # Create an Account
        storage_container_name = "storage_container"
        resp = requests.put(
            f"https://management.azure.com/subscriptions/s/resourceGroups/r/providers/Microsoft.Storage/storageAccounts/{storage_container_name}",
            timeout=2,
            json={
                "kind": "StorageV2",
                "location": "francecentral",
                "properties": {
                    "encryption": {
                        "keySource": "Microsoft.Storage",
                        "services": {"blob": {"enabled": True}},
                    }
                },
                "sku": {"name": "Standard_ZRS"},
            },
        )
        assert resp.status_code == 202
        assert "Location" in resp.headers

        # Async Operation - verify we can follow the redirect
        resp = requests.get(resp.headers["Location"], timeout=2)
        assert resp.status_code == 200
        assert resp.json()["name"] == storage_container_name

        # list returns something
        resp = requests.get(
            "https://management.azure.com/subscriptions/s/providers/Microsoft.Storage/storageAccounts",
            timeout=2,
        )
        assert resp.status_code == 200
        assert len(resp.json()["value"]) == 1
        assert resp.json()["value"][0]["name"] == storage_container_name

    def test_list_keys(self) -> None:
        # Create an Account
        storage_container_name = "storage_container"
        requests.put(
            f"https://management.azure.com/subscriptions/s/resourceGroups/r/providers/Microsoft.Storage/storageAccounts/{storage_container_name}",
            timeout=2,
            json={
                "kind": "StorageV2",
                "location": "francecentral",
                "properties": {
                    "encryption": {
                        "keySource": "Microsoft.Storage",
                        "services": {"blob": {"enabled": True}},
                    }
                },
                "sku": {"name": "Standard_ZRS"},
            },
        )

        # Verify we can retrieve the Access Keys
        resp = requests.post(
            f"https://management.azure.com/subscriptions/s/resourceGroups/r/providers/Microsoft.Storage/storageAccounts/{storage_container_name}/listKeys?api-version=2023-01-01&$expand=kerb",
            timeout=2,
        )

        assert resp.status_code == 200
        assert len(resp.json()["keys"]) == 2
