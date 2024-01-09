from ...mazure_core import ResponseType
from .subscriptions.response import SubscriptionResponse


class ManagementResponse:
    def process_request(self, path: str, method: str) -> ResponseType:
        assert path.startswith("/subscriptions")
        assert method == "GET"
        subscription_id = path.split("/")[2]

        return SubscriptionResponse(subscription_id).get_locations()
