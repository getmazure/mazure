import os
from base64 import b64encode
from datetime import datetime
from typing import Any, Dict

from peewee import DateTimeField, ForeignKeyField, Model, TextField


def _random_value() -> bytes:
    return b64encode(os.urandom(25))


class StorageAccountKey(Model):  # type: ignore[misc]
    created_on = DateTimeField(default=datetime.now)
    key_name = TextField()
    value = TextField(default=_random_value)


class StorageAccount(Model):  # type: ignore[misc]
    subscription_id = TextField()
    resource_group = TextField()
    name = TextField()
    location = TextField()
    storage_kind = TextField()
    sku = TextField()

    def to_json(self) -> Dict[str, Any]:
        keys = (
            StorageAccountKey.select()
            .join(StorageAccountKeyLink)
            .join(StorageAccount)
            .where(StorageAccount.id == self.id)  # pylint: disable=no-member
        )
        return {
            "id": f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.Storage/storageAccounts/{self.name}",
            "kind": self.storage_kind,
            "location": self.location,
            "name": self.name,
            "properties": {
                "accessTier": "Hot",
                "allowBlobPublicAccess": False,
                "allowCrossTenantReplication": False,
                "creationTime": "2024-01-21T18:54:32.3302525Z",
                "encryption": {
                    "keySource": "Microsoft.Storage",
                    "services": {
                        "blob": {
                            "enabled": True,
                            "keyType": "Account",
                            "lastEnabledTime": "2024-01-21T18:54:32.4239801Z",
                        },
                        "file": {
                            "enabled": True,
                            "keyType": "Account",
                            "lastEnabledTime": "2024-01-21T18:54:32.4239801Z",
                        },
                    },
                },
                "keyCreationTime": {
                    k.key_name: k.created_on.strftime("%Y-%m-%dT%H:%M:%S:%sZ")
                    for k in keys
                },
                "minimumTlsVersion": "TLS1_0",
                "networkAcls": {
                    "bypass": "AzureServices",
                    "defaultAction": "Allow",
                    "ipRules": [],
                    "ipv6Rules": [],
                    "virtualNetworkRules": [],
                },
                "primaryEndpoints": {
                    "blob": f"https://{self.name}.blob.core.windows.net/",
                    "dfs": f"https://{self.name}.dfs.core.windows.net/",
                    "file": f"https://{self.name}.file.core.windows.net/",
                    "queue": f"https://{self.name}.queue.core.windows.net/",
                    "table": f"https://{self.name}.table.core.windows.net/",
                    "web": f"https://{self.name}.z28.web.core.windows.net/",
                },
                "primaryLocation": self.location,
                "privateEndpointConnections": [],
                "provisioningState": "Succeeded",
                "statusOfPrimary": "available",
                "supportsHttpsTrafficOnly": True,
            },
            "sku": {"name": self.sku, "tier": "Standard"},
            "tags": {},
            "type": "Microsoft.Storage/storageAccounts",
        }


class StorageAccountKeyLink(Model):  # type: ignore[misc]
    key = ForeignKeyField(StorageAccountKey)
    account = ForeignKeyField(StorageAccount)
