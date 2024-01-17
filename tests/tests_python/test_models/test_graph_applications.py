from mazure.azure_services.management.graph.models import graph_backend

# Fixtures are applied automatically, but we do have to load them
from .. import reset_data  # pylint: disable=W0611


def test_applications_lifecycle() -> None:
    assert graph_backend.list_applications() == []

    app = graph_backend.create_application("app_name")

    dct = app.to_json()
    assert dct["createdDateTime"]
    assert dct["displayName"] == "app_name"

    assert len(graph_backend.list_applications()) == 1
