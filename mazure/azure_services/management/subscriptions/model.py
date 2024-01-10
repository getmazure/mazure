from typing import List, TypedDict
from uuid import uuid4

from .data.locations import LocationType, locations


class CountType(TypedDict):
    type: str
    value: int


class SubscriptionPolicyType(TypedDict):
    locationPlacementId: str
    quotaId: str
    spendingLimit: str


class SubscriptionPromotionType(TypedDict):
    category: str
    endDateTime: str


class SubscriptionType(TypedDict):
    authorizationSource: str
    displayName: str
    id: str
    managedByTenants: List[str]
    promotions: List[SubscriptionPromotionType]
    state: str
    subscriptionId: str
    subscriptionPolicies: SubscriptionPolicyType
    tenantId: str


class SubscriptionResponseType(TypedDict):
    count: CountType
    value: List[SubscriptionType]


class SubscriptionModel:
    def __init__(self) -> None:
        self.subscription_id = str(uuid4())
        self.tenant_id = str(uuid4())

    def get_subscriptions(self) -> SubscriptionResponseType:
        return {
            "count": {"type": "Total", "value": 1},
            "value": [
                {
                    "authorizationSource": "RoleBased",
                    "displayName": "Azure subscription 1",
                    "id": f"/subscriptions/{self.subscription_id}",
                    "managedByTenants": [],
                    "promotions": [
                        {
                            "category": "freetier",
                            "endDateTime": "2025-02-08T21:34:06.7548166Z",
                        }
                    ],
                    "state": "Enabled",
                    "subscriptionId": self.subscription_id,
                    "subscriptionPolicies": {
                        "locationPlacementId": "Public_2014-09-01",
                        "quotaId": "FreeTrial_2014-09-01",
                        "spendingLimit": "On",
                    },
                    "tenantId": self.tenant_id,
                }
            ],
        }

    def get_locations(self) -> List[LocationType]:
        return locations
