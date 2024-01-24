from peewee import SqliteDatabase

from ..azure_services.management.graph.models.application import Application
from ..azure_services.management.resource_groups.model import ResourceGroup
from ..azure_services.management.storage.models.async_operation import (
    AsyncStorageOperation,
)
from ..azure_services.management.storage.models.storage_account import (
    StorageAccount,
    StorageAccountKey,
    StorageAccountKeyLink,
)
from ..azure_services.management.subscriptions.model import Subscription
from ..azure_services.storage.models.blob import Blob
from ..azure_services.storage.models.storage_container import StorageContainer
from .login import responses as login_responses
from .management.graph import responses as graph_responses
from .management.operation_results import responses as operation_result_responses
from .management.resource_groups import responses as resource_group_responses
from .management.storage import responses as storage_management_responses
from .management.subscriptions import responses as subscription_response
from .storage import responses as storage_responses

tables = [
    Application,
    AsyncStorageOperation,
    Blob,
    ResourceGroup,
    StorageAccount,
    StorageAccountKey,
    StorageAccountKeyLink,
    StorageContainer,
    Subscription,
]

db = SqliteDatabase("/tmp/mazure.db")

db.bind(tables)
db.create_tables(tables)
