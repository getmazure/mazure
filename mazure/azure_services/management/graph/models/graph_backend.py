# PeeWee does not support typing
# https://github.com/coleifer/peewee/issues/1298

from typing import Any, Dict, List, Optional

from .application import Application, DeletedApplication


def get_application(app_object_id: str) -> Optional[Application]:
    return Application.get_or_none(Application.app_object_id == app_object_id)  # type: ignore[no-any-return]


def get_application_by_app_id(app_id: str) -> Optional[Application]:
    return Application.get_or_none(Application.app_id == app_id)  # type: ignore[no-any-return]


def update_application(
    app_object_id: str, deeds: Dict[str, Any]
) -> Optional[Application]:
    app = get_application(app_object_id)
    if app is not None:
        app.update_details(deeds)
    return app


def update_application_by_app_id(
    app_id: str, deeds: Dict[str, Any]
) -> Optional[Application]:
    app = get_application_by_app_id(app_id)
    if app is not None:
        app.update_details(deeds)
    return app


def list_applications() -> List["Application"]:
    return Application.select()  # type: ignore[no-any-return]


def list_deleted_applications() -> List["DeletedApplication"]:
    return DeletedApplication.select()  # type: ignore[no-any-return]


def create_application(name: str) -> "Application":
    return Application.create(name=name)  # type: ignore[no-any-return]


def delete_application(
    app_object_id: Optional[str] = None, app_id: Optional[str] = None
) -> None:
    if app_object_id:
        app = Application.get_by_id(app_object_id)
        DeletedApplication.create(
            app_object_id=app_object_id, app_id=app.app_id, name=app.name
        )
        app.delete_instance()
    if app_id:
        app = Application.get(Application.app_id == app_id)
        DeletedApplication.create(
            app_object_id=app.app_object_id, app_id=app.app_id, name=app.name
        )
        app.delete_instance()
