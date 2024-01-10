import json

from mazure.mazure_core import ResponseType

from .model import SubscriptionModel


class SubscriptionResponse:
    def __init__(self) -> None:
        self.model = SubscriptionModel()

    def get_subscriptions(self) -> ResponseType:
        response = json.dumps(self.model.get_subscriptions())

        return 200, {}, response.encode("utf-8")

    def get_locations(self, subscription_id: str) -> ResponseType:
        content = self.model.get_locations()
        response = json.dumps({"value": content})

        response = response.replace("__SUBID__", subscription_id)

        return 200, {}, response.encode("utf-8")
