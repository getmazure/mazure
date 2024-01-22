from uuid import uuid4

from peewee import Model, TextField, UUIDField


class AsyncStorageOperation(Model):  # type: ignore[misc]
    id = UUIDField(primary_key=True, default=uuid4)
    t = TextField()
    h = TextField()
    c = TextField()
    s = TextField()
    storage_account_id = TextField()
