from typing import List, TypedDict
from uuid import uuid4

from peewee import Model, UUIDField


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


class Subscription(Model):  # type: ignore
    id = UUIDField(primary_key=True, default=uuid4)
    tenant_id = UUIDField(default=uuid4)

    def to_json(self) -> SubscriptionType:
        return {
            "authorizationSource": "RoleBased",
            "displayName": "Azure subscription 1",
            "id": f"/subscriptions/{str(self.id)}",
            "managedByTenants": [],
            "promotions": [
                {
                    "category": "freetier",
                    "endDateTime": "2025-02-08T21:34:06.7548166Z",
                }
            ],
            "state": "Enabled",
            "subscriptionId": str(self.id),
            "subscriptionPolicies": {
                "locationPlacementId": "Public_2014-09-01",
                "quotaId": "FreeTrial_2014-09-01",
                "spendingLimit": "On",
            },
            "tenantId": str(self.tenant_id),
        }
