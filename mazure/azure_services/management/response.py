import re
from urllib.parse import urlparse

from ...mazure_core import ResponseType
from .resource_groups.response import ResourceGroupsResponse
from .subscriptions.response import SubscriptionResponse

ListSubscriptionsPattern = re.compile("^/subscriptions$")
LocationsPattern = re.compile("^/subscriptions/[-a-z0-9A-Z]+/locations$")
ListResourceGroupsPattern = re.compile("^/subscriptions/[-a-z0-9A-Z]+/resourcegroups$")
ResourceGroupPattern = re.compile(
    "^/subscriptions/[-a-z0-9A-Z]+/resourcegroups/[-_a-z0-9A-Z]+$"
)
OperationResultPattern = re.compile(
    "^/subscriptions/[-a-z0-9A-Z]+/operationresults/[-_a-z0-9A-Z]+$"
)


class ManagementResponse:
    def process_request(self, path: str, method: str, body: bytes) -> ResponseType:
        parsed = urlparse(path)

        if re.match(ListSubscriptionsPattern, parsed.path) and method == "GET":
            return SubscriptionResponse().get_subscriptions()

        if re.match(LocationsPattern, parsed.path) and method == "GET":
            # query could include includeExtendedLocations=true
            # But that returns the same result AFAICS
            subscription_id = path.split("/")[2]
            return SubscriptionResponse().get_locations(subscription_id)

        if re.match(ResourceGroupPattern, parsed.path) and method == "PUT":
            subscription_id = parsed.path.split("/")[-3]
            name = parsed.path.split("/")[-1]
            return ResourceGroupsResponse().create_resource_group(
                subscription_id, name=name, body=body
            )

        if re.match(ResourceGroupPattern, parsed.path) and method == "HEAD":
            subscription_id = parsed.path.split("/")[-3]
            name = parsed.path.split("/")[-1]
            return ResourceGroupsResponse().has_resource_group(name=name)

        if re.match(ResourceGroupPattern, parsed.path) and method == "GET":
            subscription_id = parsed.path.split("/")[-3]
            name = parsed.path.split("/")[-1]
            return ResourceGroupsResponse().get_resource_group(
                subscription_id, name=name
            )

        if re.match(ResourceGroupPattern, parsed.path) and method == "DELETE":
            subscription_id = parsed.path.split("/")[-3]
            name = parsed.path.split("/")[-1]
            return ResourceGroupsResponse().delete_resource_group(
                subscription_id, name=name
            )

        if re.match(ListResourceGroupsPattern, parsed.path) and method == "GET":
            subscription_id = parsed.path.split("/")[-2]
            return ResourceGroupsResponse().list_resource_groups(subscription_id)

        if re.match(OperationResultPattern, parsed.path) and method == "GET":
            return 200, {}, b""

        return 500, {}, b"NotYetImplemented"
