import json
import random
import re
import string

from mazure.mazure_core import MazureRequest, ResponseType
from mazure.mazure_core.route_mapping import register

from .models.async_operation import AsyncStorageOperation
from .models.storage_account import (
    StorageAccount,
    StorageAccountKey,
    StorageAccountKeyLink,
)


@register(
    host="https://management.azure.com",
    path=re.compile(
        "/subscriptions/[-a-z0-9A-Z]+/providers/Microsoft.Storage/checkNameAvailability"
    ),
    method="POST",
)
def check_name_availability(request: MazureRequest) -> ResponseType:
    name = json.loads(request.body)["name"]
    StorageAccount.table_exists()
    user = StorageAccount.select().where(StorageAccount.name == name)
    if user.exists():
        resp = {
            "message": f"The storage account named {name} is already taken.",
            "nameAvailable": False,
            "reason": "AlreadyExists",
        }
    else:
        resp = {"nameAvailable": True}
    return 200, {}, json.dumps(resp).encode("utf-8")


@register(
    host="https://management.azure.com",
    path=re.compile(
        "/subscriptions/[-a-z0-9A-Z]+/resourceGroups/[-a-z0-9A-Z]+/providers/Microsoft.Storage/storageAccounts/[-_a-z0-9A-Z]+"
    ),
    method="PUT",
)
def create_storage_account(request: MazureRequest) -> ResponseType:
    # TODO: validate ResourceGroup exists
    url_parts = request.parsed_path.path.split("/")
    subscription_id = url_parts[1]
    body = json.loads(request.body)
    location = body["location"]
    storage_account = StorageAccount.create(
        subscription_id=subscription_id,
        resource_group=url_parts[3],
        name=url_parts[-1],
        location=location,
        storage_kind=body["kind"],
        sku=body["sku"]["name"],
    )
    key1 = StorageAccountKey.create(key_name="key1")
    key2 = StorageAccountKey.create(key_name="key2")
    StorageAccountKeyLink.create(key=key1, account=storage_account)
    StorageAccountKeyLink.create(key=key2, account=storage_account)
    t = "".join(random.choices(string.digits, k=18))
    h = "".join(random.choices(string.digits + string.ascii_letters, k=43))
    c = "".join(random.choices(string.digits + string.ascii_letters + "-_", k=2395))
    s = "".join(random.choices(string.digits + string.ascii_letters + "-_", k=342))
    async_op = AsyncStorageOperation.create(
        t=t,
        h=h,
        c=c,
        s=s,
        storage_account_id=storage_account.id,  # pylint: disable=no-member
    )
    location = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Storage/locations/{location}/asyncoperations/{async_op.id}?monitor=true&api-version=2023-01-01&t={t}&c={c}&s={s}&h={h}"
    headers = {
        "Content-Type": "text/plain; charset=utf-8",
        "Expires": "-1",
        "Location": location,
        "Retry-After": "3",
    }
    return 202, headers, b""


@register(
    host="https://management.azure.com",
    path=re.compile(
        "/subscriptions/[-a-z0-9A-Z]+/providers/Microsoft.Storage/locations/[-a-z0-9A-Z]+/asyncoperations/[-a-z0-9A-Z]+"
    ),
    method="GET",
)
def get_result_async_operation(request: MazureRequest) -> ResponseType:
    async_id = request.parsed_path.path.split("/")[-1]
    op = AsyncStorageOperation.get_by_id(async_id)

    # Validation
    query_args = request.parsed_path.query.split("&")
    t = [arg for arg in query_args if arg.startswith("t=")][0].split("=")[-1]
    c = [arg for arg in query_args if arg.startswith("c=")][0].split("=")[-1]
    s = [arg for arg in query_args if arg.startswith("s=")][0].split("=")[-1]
    h = [arg for arg in query_args if arg.startswith("h=")][0].split("=")[-1]
    assert op.t == t
    assert op.c == c
    assert op.s == s
    assert op.h == h

    storage_account = StorageAccount.get_by_id(op.storage_account_id)
    return 200, {}, json.dumps(storage_account.to_json()).encode("utf-8")


@register(
    host="https://management.azure.com",
    path=re.compile(
        "/subscriptions/[-a-z0-9A-Z]+/providers/Microsoft.Storage/storageAccounts"
    ),
    method="GET",
)
def get_storage_accounts(
    request: MazureRequest,  # pylint: disable=unused-argument
) -> ResponseType:
    # TODO: only return StorageAccounts in current Subscription
    accounts = StorageAccount.select()
    return (
        200,
        {},
        json.dumps({"value": [acc.to_json() for acc in accounts]}).encode("utf-8"),
    )


@register(
    host="https://management.azure.com",
    path=re.compile(
        "/subscriptions/[-a-z0-9A-Z]+/resourceGroups/[-a-z0-9A-Z]+/providers/Microsoft.Storage/storageAccounts/[-_a-z0-9A-Z]+/listKeys"
    ),
    method="POST",
)
def list_keys(request: MazureRequest) -> ResponseType:
    name = request.parsed_path.path.split("/")[-2]
    keys = (
        StorageAccountKey.select()
        .join(StorageAccountKeyLink)
        .join(StorageAccount)
        .where(StorageAccount.name == name)
    )

    # Format:
    resp = [
        {
            "creationTime": k.created_on.strftime("%Y-%m-%dT%H:%M:%S:%sZ"),
            "keyName": k.key_name,
            "permissions": "FULL",
            "value": k.value,
        }
        for k in keys
    ]
    return 200, {}, json.dumps({"keys": resp}).encode("utf-8")
