import json
import random
import string

from mazure.mazure_core import ResponseType

from . import model


class ResourceGroupsResponse:
    def __init__(self) -> None:
        pass

    def create_resource_group(
        self, subscription_id: str, name: str, body: bytes
    ) -> ResponseType:
        location = json.loads(body)["location"]
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

    def has_resource_group(self, name: str) -> ResponseType:
        if model.has_resource_group(name):
            return 204, {}, b""
        return 404, {}, b""

    def get_resource_group(self, subscription_id: str, name: str) -> ResponseType:
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

    def delete_resource_group(self, subscription_id: str, name: str) -> ResponseType:
        model.resource_groups.pop(name)
        options = string.ascii_letters + string.digits
        operation_result = "".join(random.choices(options, k=122))
        t = "".join(random.choices(string.digits, k=18))
        c = "".join(random.choices(options, k=2395))
        s = "".join(random.choices(options, k=342))
        h = "".join(random.choices(options, k=43))
        location = f"https://management.azure.com/subscriptions/{subscription_id}/operationresults/{operation_result}?api-version=2022-09-01&t={t}&c={c}&s={s}&h={h}"
        return 202, {"Location": location}, b""

    def list_resource_groups(self, subscription_id: str) -> ResponseType:
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
