import json

import requests
from peewee import SqliteDatabase

from mazure.azure_services.management.resource_groups.model import ResourceGroup

# Fixtures are applied automatically, but we do have to load them
from .. import load_responses  # pylint: disable=W0611

MODELS = [ResourceGroup]

# use an in-memory SQLite for tests.
_test_db = SqliteDatabase(":memory:")


class TestResourceGroups:
    def setup_method(self) -> None:
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        _test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        _test_db.connect()
        _test_db.create_tables(MODELS)

    def teardown_method(self) -> None:
        _test_db.drop_tables(MODELS)

        # Close connection to db.
        _test_db.close()

    def test_list_resource_groups(self) -> None:
        resp = requests.get(
            "https://management.azure.com/subscriptions/mysub/resourcegroups", timeout=2
        )

        assert resp.status_code == 200
        assert "application/json" in resp.headers["Content-Type"]

        assert json.loads(resp.content) == {"value": []}

    def test_create_and_get_application(self) -> None:
        url = "https://management.azure.com/subscriptions/mysub/resourcegroups/my_rg"
        request_body = {"location": "lisboa"}
        resp = requests.put(url, json=request_body, timeout=2)

        assert resp.status_code == 201
        body = json.loads(resp.content.decode("utf-8"))
        assert body["location"] == "lisboa"
        assert body["id"] == "/subscriptions/mysub/resourceGroups/my_rg"
        assert body["name"] == "my_rg"

        resp = requests.get(url, timeout=2)
        assert resp.status_code == 200
        body = json.loads(resp.content.decode("utf-8"))
        assert body["location"] == "lisboa"
        assert body["id"] == "/subscriptions/mysub/resourceGroups/my_rg"
        assert body["name"] == "my_rg"

        resp = requests.get(
            "https://management.azure.com/subscriptions/mysub/resourcegroups", timeout=2
        )

        assert len(json.loads(resp.content)["value"]) == 1

    def test_resource_group_exists(self) -> None:
        url = "https://management.azure.com/subscriptions/mysub/resourcegroups/my_rg"
        resp = requests.head(url, timeout=2)
        assert resp.status_code == 404

        request_body = {"location": "lisboa"}
        requests.put(url, json=request_body, timeout=2)

        resp = requests.head(url, timeout=2)
        assert resp.status_code == 204

    def test_delete_resource_group(self) -> None:
        url = "https://management.azure.com/subscriptions/mysub/resourcegroups/my_rg"
        request_body = {"location": "lisboa"}
        resp = requests.put(url, json=request_body, timeout=2)

        requests.delete(url=url, timeout=2)

        # List is Empty
        resp = requests.get(
            "https://management.azure.com/subscriptions/mysub/resourcegroups", timeout=2
        )
        assert json.loads(resp.content) == {"value": []}

        # ResourceGroup does not exist
        resp = requests.head(url, timeout=2)
        assert resp.status_code == 404
