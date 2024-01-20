from unittest import TestCase

from peewee import SqliteDatabase

from mazure.azure_services.management.graph.models import graph_backend
from mazure.azure_services.management.graph.models.application import (
    Application,
    DeletedApplication,
)

MODELS = [Application, DeletedApplication]

# use an in-memory SQLite for tests.
test_db = SqliteDatabase(":memory:")


class TestGraphApplications(TestCase):
    def setUp(self) -> None:
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        test_db.connect()
        test_db.create_tables(MODELS)

    def tearDown(self) -> None:
        test_db.drop_tables(MODELS)

        # Close connection to db.
        test_db.close()

    def test_applications_lifecycle(self) -> None:
        assert not graph_backend.list_applications()

        app = graph_backend.create_application("app_name")

        dct = app.to_json()
        assert dct["createdDateTime"]
        assert dct["displayName"] == "app_name"

        assert len(graph_backend.list_applications()) == 1

        graph_backend.delete_application(app_object_id=dct["id"])

        assert not graph_backend.list_applications()

        assert len(graph_backend.list_deleted_applications()) == 1
