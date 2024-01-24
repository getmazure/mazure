from typing import Any, Dict
from uuid import uuid4

from peewee import Model, TextField, UUIDField


class ResourceGroup(Model):  # type: ignore[misc]
    id = UUIDField(primary_key=True, default=uuid4)
    subscription_id = TextField()
    name = TextField()
    location = TextField()

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": f"/subscriptions/{self.subscription_id}/resourceGroups/{self.name}",
            "location": self.location,
            "name": self.name,
            "properties": {"provisioningState": "Succeeded"},
            "type": "Microsoft.Resources/resourceGroups",
        }
