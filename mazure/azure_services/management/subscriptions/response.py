import json
from typing import Any, Dict, Tuple

from .model import SubscriptionModel


class SubscriptionResponse:
    def __init__(self, subscription_id: str):
        self.model = SubscriptionModel()
        self.subscription_id = subscription_id

    def get_locations(self) -> Tuple[int, Dict[str, Any], bytes]:
        content = self.model.get_locations()
        response = json.dumps({"value": content})

        response = response.replace("__SUBID__", self.subscription_id)

        return 200, {}, response.encode("utf-8")
