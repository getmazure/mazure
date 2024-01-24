import json
import random
import string

from mazure.mazure_core import ResponseType
from mazure.mazure_core.mazure_request import MazureRequest
from mazure.mazure_core.route_mapping import register

from .. import PathSingleSubscription
from .model import ResourceGroup


@register(
    parent=PathSingleSubscription, path=r"/resourcegroups/[-_a-z0-9A-Z]+$", method="PUT"
)
def create_resource_group(request: MazureRequest) -> ResponseType:
    subscription_id = request.path.split("/")[-3]
    name = request.path.split("/")[-1]
    location = json.loads(request.body)["location"]
    rg = ResourceGroup.create(
        subscription_id=subscription_id, name=name, location=location
    )

    response = json.dumps(rg.to_json()).encode("utf-8")

    return 201, {"content-length": str(len(response))}, response


@register(
    parent=PathSingleSubscription,
    path=r"/resourcegroups/[-_a-z0-9A-Z]+$",
    method="HEAD",
)
def has_resource_group(request: MazureRequest) -> ResponseType:
    name = request.path.split("/")[-1]
    if ResourceGroup.get_or_none(ResourceGroup.name == name) is not None:
        return 204, {}, b""
    return 404, {}, b""


@register(
    parent=PathSingleSubscription, path=r"/resourcegroups/[-_a-z0-9A-Z]+$", method="GET"
)
def get_resource_group(request: MazureRequest) -> ResponseType:
    subscription_id = request.path.split("/")[-3]
    name = request.path.split("/")[-1]
    rg = ResourceGroup.get_or_none(
        ResourceGroup.subscription_id == subscription_id, ResourceGroup.name == name
    )
    response = json.dumps(rg.to_json()).encode("utf-8")

    return 200, {}, response


@register(
    parent=PathSingleSubscription,
    path=r"/resourcegroups/[-_a-z0-9A-Z]+$",
    method="DELETE",
)
def delete_resource_group(request: MazureRequest) -> ResponseType:
    subscription_id = request.path.split("/")[-3]
    name = request.path.split("/")[-1]

    rg = ResourceGroup.get_or_none(
        ResourceGroup.subscription_id == subscription_id, ResourceGroup.name == name
    )
    ResourceGroup.delete_by_id(rg.id)

    options = string.ascii_letters + string.digits
    operation_result = "".join(random.choices(options, k=122))
    t = "".join(random.choices(string.digits, k=18))
    c = "".join(random.choices(options, k=2395))
    s = "".join(random.choices(options, k=342))
    h = "".join(random.choices(options, k=43))
    location = f"https://management.azure.com/subscriptions/{subscription_id}/operationresults/{operation_result}?api-version=2022-09-01&t={t}&c={c}&s={s}&h={h}"
    return 202, {"Location": location}, b""


@register(parent=PathSingleSubscription, path=r"/resourcegroups$", method="GET")
def list_resource_groups(request: MazureRequest) -> ResponseType:
    subscription_id = request.path.split("/")[-2]
    all_resource_groups = ResourceGroup.select().where(
        ResourceGroup.subscription_id == subscription_id
    )
    rgs = [rg.to_json() for rg in all_resource_groups]  # pylint: disable=E1133
    response = json.dumps({"value": rgs}).encode("utf-8")

    return 200, {"Content-Type": "application/json"}, response
