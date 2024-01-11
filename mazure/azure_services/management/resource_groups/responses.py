import json
import random
import re
import string

from mazure.mazure_core import MazureRequest, ResponseType
from mazure.mazure_core.route_mapping import register

from . import model


@register(
    "https://management.azure.com",
    path=re.compile("^/subscriptions/[-a-z0-9A-Z]+/resourcegroups/[-_a-z0-9A-Z]+$"),
    method="PUT",
)
def create_resource_group(request: MazureRequest) -> ResponseType:
    subscription_id = request.path.split("/")[-3]
    name = request.path.split("/")[-1]
    location = json.loads(request.body)["location"]
    model.create_resource_group(name, location)

    data = {
        "id": f"/subscriptions/{subscription_id}/resourceGroups/{name}",
        "location": location,
        "name": name,
        "properties": {"provisioningState": "Succeeded"},
        "type": "Microsoft.Resources/resourceGroups",
    }
    response = json.dumps(data).encode("utf-8")

    return 201, {"content-length": len(response)}, response


@register(
    "https://management.azure.com",
    path=re.compile("^/subscriptions/[-a-z0-9A-Z]+/resourcegroups/[-_a-z0-9A-Z]+$"),
    method="HEAD",
)
def has_resource_group(request: MazureRequest) -> ResponseType:
    name = request.path.split("/")[-1]
    if model.has_resource_group(name):
        return 204, {}, b""
    return 404, {}, b""


@register(
    "https://management.azure.com",
    path=re.compile("^/subscriptions/[-a-z0-9A-Z]+/resourcegroups/[-_a-z0-9A-Z]+$"),
    method="GET",
)
def get_resource_group(request: MazureRequest) -> ResponseType:
    subscription_id = request.path.split("/")[-3]
    name = request.path.split("/")[-1]
    location = model.resource_groups[name]
    data = {
        "id": f"/subscriptions/{subscription_id}/resourceGroups/{name}",
        "location": location,
        "name": name,
        "properties": {"provisioningState": "Succeeded"},
        "type": "Microsoft.Resources/resourceGroups",
    }
    response = json.dumps(data).encode("utf-8")

    return 200, {}, response


@register(
    "https://management.azure.com",
    path=re.compile("^/subscriptions/[-a-z0-9A-Z]+/resourcegroups/[-_a-z0-9A-Z]+$"),
    method="DELETE",
)
def delete_resource_group(request: MazureRequest) -> ResponseType:
    subscription_id = request.path.split("/")[-3]
    name = request.path.split("/")[-1]
    model.resource_groups.pop(name)
    options = string.ascii_letters + string.digits
    operation_result = "".join(random.choices(options, k=122))
    t = "".join(random.choices(string.digits, k=18))
    c = "".join(random.choices(options, k=2395))
    s = "".join(random.choices(options, k=342))
    h = "".join(random.choices(options, k=43))
    location = f"https://management.azure.com/subscriptions/{subscription_id}/operationresults/{operation_result}?api-version=2022-09-01&t={t}&c={c}&s={s}&h={h}"
    return 202, {"Location": location}, b""


@register(
    "https://management.azure.com",
    path=re.compile("^/subscriptions/[-a-z0-9A-Z]+/resourcegroups$"),
    method="GET",
)
def list_resource_groups(request: MazureRequest) -> ResponseType:
    subscription_id = request.path.split("/")[-2]
    groups = [
        {
            "id": f"/subscriptions/{subscription_id}/resourceGroups/{name}",
            "location": location,
            "name": name,
            "properties": {"provisioningState": "Succeeded"},
            "type": "Microsoft.Resources/resourceGroups",
        }
        for name, location in model.resource_groups.items()
    ]
    response = json.dumps({"value": groups}).encode("utf-8")

    return 200, {}, response