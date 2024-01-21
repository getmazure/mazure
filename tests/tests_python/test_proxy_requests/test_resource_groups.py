from typing import Any
from uuid import uuid4

import requests

from . import skip_if_proxy_not_configured  # pylint: disable=W0611


def test_resource_group_lifecycle(
    skip_if_proxy_not_configured: Any,  # pylint: disable=W0613, W0621
) -> None:
    sub = uuid4()
    rg_name = "my_resource_group"
    url = f"https://management.azure.com/subscriptions/{sub}/resourcegroups/{rg_name}?api-version=2022-09-01"
    headers = {"CommandName": "group create"}
    resp = requests.put(
        url, timeout=2, headers=headers, json={"location": "westeurope"}
    )

    assert resp.status_code == 201
    assert "Content-Encoding" not in resp.headers
    assert resp.json() == {
        "id": f"/subscriptions/{sub}/resourceGroups/{rg_name}",
        "location": "westeurope",
        "name": rg_name,
        "properties": {"provisioningState": "Succeeded"},
        "type": "Microsoft.Resources/resourceGroups",
    }

    # EXISTS
    url = f"https://management.azure.com/subscriptions/{sub}/resourcegroups/{rg_name}?api-version=2022-09-01"
    headers = {"CommandName": "group exists"}
    resp = requests.head(url, timeout=2, headers=headers)

    assert resp.status_code == 204

    # EXISTS - UNKNOWN
    url = f"https://management.azure.com/subscriptions/{sub}/resourcegroups/sth?api-version=2022-09-01"
    headers = {"CommandName": "group exists"}
    resp = requests.head(url, timeout=2, headers=headers)

    assert resp.status_code == 404

    # SHOW
    url = f"https://management.azure.com/subscriptions/{sub}/resourcegroups/{rg_name}?api-version=2022-09-01"
    headers = {"CommandName": "group show"}
    resp = requests.get(url, timeout=2, headers=headers)

    assert resp.status_code == 200
    assert resp.headers.get("Content-Encoding") == "gzip"
    assert resp.json() == {
        "id": f"/subscriptions/{sub}/resourceGroups/{rg_name}",
        "location": "westeurope",
        "name": rg_name,
        "properties": {"provisioningState": "Succeeded"},
        "type": "Microsoft.Resources/resourceGroups",
    }

    # LIST
    url = f"https://management.azure.com/subscriptions/{sub}/resourcegroups?api-version=2022-09-01"
    headers = {"CommandName": "group list"}
    resp = requests.get(url, timeout=2, headers=headers)

    assert resp.status_code == 200
    assert resp.headers.get("Content-Encoding") == "gzip"
    assert resp.json() == {
        "value": [
            {
                "id": f"/subscriptions/{sub}/resourceGroups/{rg_name}",
                "location": "westeurope",
                "name": rg_name,
                "properties": {"provisioningState": "Succeeded"},
                "type": "Microsoft.Resources/resourceGroups",
            }
        ]
    }

    # DELETE
    url = f"https://management.azure.com/subscriptions/{sub}/resourcegroups/{rg_name}?api-version=2022-09-01"
    headers = {"CommandName": "group delete"}
    resp = requests.delete(url, timeout=2, headers=headers)

    assert resp.status_code == 202
    delete_location = resp.headers["Location"]

    # Location should have multiple parameters
    # Exact value is not that important
    assert delete_location.startswith(
        f"https://management.azure.com/subscriptions/{sub}/operationresults/"
    )
    assert "&t=" in delete_location
    assert "&c=" in delete_location
    assert "&h=" in delete_location

    # CHECK IF DELETE WAS SUCCESSFUL
    headers = {"CommandName": "group delete"}
    resp = requests.get(delete_location, timeout=2, headers=headers)

    # Azure may take some time
    # If the request is still ongoing, the GET request could also return a 202 with a Location set, indicating we should retry again
    # Mazure is quick enough to not need any retries though
    assert resp.status_code == 200
    assert resp.headers.get("Location") is None
