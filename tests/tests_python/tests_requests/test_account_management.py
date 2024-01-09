from uuid import uuid4

import requests


# https://learn.microsoft.com/en-us/rest/api/resources/subscriptions/list-locations?view=rest-resources-2022-12-01&tabs=HTTP
def test_list_locations() -> None:
    sub = uuid4()
    url = f"https://management.azure.com/subscriptions/{sub}/locations?api-version=2022-12-01"
    headers = {"Accept-Encoding": "gzip, deflate"}
    resp = requests.get(url, headers=headers, timeout=2)

    assert "x-ms-request-id" in resp.headers
    assert "application/json" in resp.headers["Content-Type"]

    data = resp.json()
    assert "value" in data

    locations = data["value"]
    assert len(locations) > 50

    regions = [loc["name"] for loc in locations if loc["type"] == "Region"]
    assert "eastus" in regions
    assert "northeurope" in regions
