"""
https://learn.microsoft.com/en-us/graph/api/resources/application?view=graph-rest-1.0
"""

import io
import json
from uuid import uuid4

import pytest
import requests

from mazure.mazure_proxy.utils import read_chunked_body

# Fixtures are applied automatically, but we do have to load them
from .. import load_responses, reset_data  # pylint: disable=W0611


def test_list_application() -> None:
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
def test_create_and_get_application(get_url: str, var: str) -> None:
    request_body = {"displayName": "app_name"}
    resp = requests.post(
        "https://graph.microsoft.com/v1.0/applications", json=request_body, timeout=2
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


def test_get_application__unknown() -> None:
    url = "https://graph.microsoft.com/v1.0/applications/unknown"
    assert requests.get(url, timeout=2).status_code == 404


@pytest.mark.parametrize(
    "patch_url,var",
    [
        ("https://graph.microsoft.com/v1.0/applications/{}", "id"),
        ("https://graph.microsoft.com/v1.0/applications(appId='{}')", "appId"),
    ],
)
def test_update_application(patch_url: str, var: str) -> None:
    request_body = {"displayName": "app_name"}
    resp = requests.post(
        "https://graph.microsoft.com/v1.0/applications", json=request_body, timeout=2
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
def test_delete_application(patch_url: str, var: str) -> None:
    request_body = {"displayName": "app_name"}
    resp = requests.post(
        "https://graph.microsoft.com/v1.0/applications", json=request_body, timeout=2
    )
    body = json.loads(read_chunked_body(io.BytesIO(resp.content)).decode("utf-8"))

    resp = requests.delete(patch_url.format(body[var]), timeout=2)
    assert resp.status_code == 204

    resp = requests.get("https://graph.microsoft.com/v1.0/applications", timeout=2)
    assert resp.status_code == 200

    body = json.loads(read_chunked_body(io.BytesIO(resp.content)).decode("utf-8"))
    assert body["value"] == []


def test_deleted_applications() -> None:
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
        "https://graph.microsoft.com/v1.0/applications", json=request_body, timeout=2
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
