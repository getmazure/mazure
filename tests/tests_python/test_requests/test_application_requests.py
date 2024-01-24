"""
https://learn.microsoft.com/en-us/graph/api/resources/application?view=graph-rest-1.0
"""

import io
import json
from uuid import uuid4

import pytest
import requests
from peewee import SqliteDatabase

from mazure.azure_services.management.graph.models.application import (
    Application,
    DeletedApplication,
)
from mazure.mazure_proxy.utils import read_chunked_body

# Fixtures are applied automatically, but we do have to load them
from .. import load_responses  # pylint: disable=W0611

MODELS = [Application, DeletedApplication]

# use an in-memory SQLite for tests.
_test_db = SqliteDatabase(":memory:")


class TestGraphApplications:
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

    def test_list_application(self) -> None:
        resp = requests.get("https://graph.microsoft.com/v1.0/applications", timeout=2)

        assert resp.status_code == 200
        assert "application/json" in resp.headers["Content-Type"]

        body = json.loads(read_chunked_body(io.BytesIO(resp.content)).decode("utf-8"))
        assert "@odata.context" in body
        assert body["value"] == []

    @pytest.mark.parametrize(
        "get_url,var",
        [
            ("https://graph.microsoft.com/v1.0/applications/{}", "id"),
            ("https://graph.microsoft.com/v1.0/applications(appId='{}')", "appId"),
        ],
    )
    def test_create_and_get_application(self, get_url: str, var: str) -> None:
        request_body = {"displayName": "app_name"}
        resp = requests.post(
            "https://graph.microsoft.com/v1.0/applications",
            json=request_body,
            timeout=2,
        )

        assert resp.status_code == 200
        assert resp.headers["Transfer-Encoding"] == "chunked"

        body = json.loads(read_chunked_body(io.BytesIO(resp.content)).decode("utf-8"))
        assert body["displayName"] == "app_name"
        app_id = body["appId"]

        var_value = body[var]

        resp = requests.get(get_url.format(var_value), timeout=2)
        assert resp.status_code == 200
        assert resp.headers["Transfer-Encoding"] == "chunked"

        body = json.loads(read_chunked_body(io.BytesIO(resp.content)).decode("utf-8"))
        assert body["displayName"] == "app_name"
        assert body["appId"] == app_id

    def test_get_application__unknown(self) -> None:
        url = "https://graph.microsoft.com/v1.0/applications/unknown"
        assert requests.get(url, timeout=2).status_code == 404

    @pytest.mark.parametrize(
        "patch_url,var",
        [
            ("https://graph.microsoft.com/v1.0/applications/{}", "id"),
            ("https://graph.microsoft.com/v1.0/applications(appId='{}')", "appId"),
        ],
    )
    def test_update_application(self, patch_url: str, var: str) -> None:
        request_body = {"displayName": "app_name"}
        resp = requests.post(
            "https://graph.microsoft.com/v1.0/applications",
            json=request_body,
            timeout=2,
        )
        body = json.loads(read_chunked_body(io.BytesIO(resp.content)).decode("utf-8"))

        var_value = body[var]

        new_name = str(uuid4())[0:5]
        resp = requests.patch(
            patch_url.format(var_value), json={"displayName": new_name}, timeout=2
        )
        assert resp.status_code == 204

        resp = requests.get(patch_url.format(var_value), timeout=2)
        body = json.loads(read_chunked_body(io.BytesIO(resp.content)).decode("utf-8"))
        assert body["displayName"] == new_name

    @pytest.mark.parametrize(
        "patch_url,var",
        [
            ("https://graph.microsoft.com/v1.0/applications/{}", "id"),
            ("https://graph.microsoft.com/v1.0/applications(appId='{}')", "appId"),
        ],
    )
    def test_delete_application(self, patch_url: str, var: str) -> None:
        request_body = {"displayName": "app_name"}
        resp = requests.post(
            "https://graph.microsoft.com/v1.0/applications",
            json=request_body,
            timeout=2,
        )
        body = json.loads(read_chunked_body(io.BytesIO(resp.content)).decode("utf-8"))

        resp = requests.delete(patch_url.format(body[var]), timeout=2)
        assert resp.status_code == 204

        resp = requests.get("https://graph.microsoft.com/v1.0/applications", timeout=2)
        assert resp.status_code == 200

        body = json.loads(read_chunked_body(io.BytesIO(resp.content)).decode("utf-8"))
        assert body["value"] == []

    def test_deleted_applications(self) -> None:
        resp = requests.get(
            "https://graph.microsoft.com/directory/deleteditems/microsoft.graph.application",
            timeout=2,
        )
        body = json.loads(read_chunked_body(io.BytesIO(resp.content)).decode("utf-8"))
        assert (
            body["@odata.context"]
            == "https://graph.microsoft.com/v1.0/$metadata#applications"
        )
        assert body["value"] == []

        request_body = {"displayName": "app_name"}
        resp = requests.post(
            "https://graph.microsoft.com/v1.0/applications",
            json=request_body,
            timeout=2,
        )
        body = json.loads(read_chunked_body(io.BytesIO(resp.content)).decode("utf-8"))

        requests.delete(
            f"https://graph.microsoft.com/v1.0/applications/{body['id']}", timeout=2
        )

        resp = requests.get(
            "https://graph.microsoft.com/directory/deleteditems/microsoft.graph.application",
            timeout=2,
        )
        body = json.loads(read_chunked_body(io.BytesIO(resp.content)).decode("utf-8"))
        assert body["value"][0]["displayName"] == "app_name"
