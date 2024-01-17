from typing import List, Optional

from .application import Application

applications: List[Application] = []
deleted_applications: List[Application] = []


def list_applications() -> List[Application]:
    return applications


def list_deleted_applications() -> List[Application]:
    return deleted_applications


def create_application(name: str) -> Application:
    app = Application(name)
    applications.append(app)
    return app


def delete_application(
    app_object_id: Optional[str] = None, app_id: Optional[str] = None
) -> None:
    global applications  # pylint: disable=W0603
    if app_object_id:
        deleted_applications.extend(
            [app for app in applications if app.app_object_id == app_object_id]
        )
        applications = [
            app for app in applications if app.app_object_id != app_object_id
        ]
    if app_id:
        deleted_applications.extend(
            [app for app in applications if app.app_id == app_id]
        )
        applications = [app for app in applications if app.app_id != app_id]
