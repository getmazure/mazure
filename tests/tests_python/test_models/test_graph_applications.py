from peewee import SqliteDatabase

from mazure.azure_services.management.graph.models import graph_backend
from mazure.azure_services.management.graph.models.application import (
    Application,
    DeletedApplication,
)

MODELS = [Application, DeletedApplication]

# use an in-memory SQLite for tests.
_test_db = SqliteDatabase(":memory:")


class TestGraphApplications:
    def setup_method(self) -> None:
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        _test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        _test_db.connect()
        _test_db.create_tables(MODELS)

    def teardown_method(self) -> None:
        _test_db.drop_tables(MODELS)

        # Close connection to db.
        _test_db.close()

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
