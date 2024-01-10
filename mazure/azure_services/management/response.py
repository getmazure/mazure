from ...mazure_core import ResponseType
from .subscriptions.response import SubscriptionResponse


class ManagementResponse:
    def process_request(self, path: str, method: str) -> ResponseType:
        assert path.startswith("/subscriptions")
        assert method == "GET"
        if path == "/subscriptions?api-version=2022-12-01":
            return SubscriptionResponse().get_subscriptions()

        # query could include includeExtendedLocations=true
        # But that returns the same result AFAICS

        subscription_id = path.split("/")[2]

        return SubscriptionResponse().get_locations(subscription_id)
