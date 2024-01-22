from typing import Any, Dict, Tuple

from peewee import SqliteDatabase

from ..azure_services.management.graph.models.application import Application
from ..azure_services.management.storage.models.async_operation import (
    AsyncStorageOperation,
)
from ..azure_services.management.storage.models.storage_account import (
    StorageAccount,
    StorageAccountKey,
    StorageAccountKeyLink,
)
from ..azure_services.storage.models.blob import Blob
from ..azure_services.storage.models.storage_container import StorageContainer
from .mazure_request import MazureRequest

ResponseType = Tuple[int, Dict[str, Any], bytes]

tables = [
    Application,
    AsyncStorageOperation,
    Blob,
    StorageAccount,
    StorageAccountKey,
    StorageAccountKeyLink,
    StorageContainer,
]

db = SqliteDatabase("/tmp/mazure.db")

db.bind(tables)
db.create_tables(tables)
