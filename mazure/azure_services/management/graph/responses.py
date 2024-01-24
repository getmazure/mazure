import json
import random
import re
import string
from uuid import uuid4

from mazure.mazure_core import ResponseType
from mazure.mazure_core.mazure_request import MazureRequest
from mazure.mazure_core.route_mapping import register
from mazure.mazure_proxy.utils import chunk_body

from .. import PathGraph
from .models import graph_backend


@register(
    parent=PathGraph,
    path=r"/v1.0/applications$",
    method="GET",
)
def list_applications(
    request: MazureRequest,  # pylint: disable=unused-argument
) -> ResponseType:
    apps = graph_backend.list_applications()
    app_list = {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#applications",
        "value": [app.to_json() for app in apps],
    }
    chunk_headers = {
        "Transfer-Encoding": "chunked",
        "Content-Type": "application/json;odata.metadata=minimal;odata.streaming=true;IEEE754Compatible=false;charset=utf-8",
    }
    chunked = chunk_body(json.dumps(app_list).encode("utf-8"))
    return 200, chunk_headers, chunked


@register(
    parent=PathGraph,
    path=r"/v1.0/applications$",
    method="POST",
)
def create_application(
    request: MazureRequest,  # pylint: disable=unused-argument
) -> ResponseType:
    name = json.loads(request.body.decode("utf-8"))["displayName"]

    app = graph_backend.create_application(name)
    chunk_headers = {
        "Transfer-Encoding": "chunked",
        "Content-Type": "application/json;odata.metadata=minimal;odata.streaming=true;IEEE754Compatible=false;charset=utf-8",
    }
    chunked = chunk_body(json.dumps(app.to_json()).encode("utf-8"))
    return 200, chunk_headers, chunked


@register(
    parent=PathGraph,
    path=r"/v1.0/applications/[^/]+$",
    method="GET",
)
def get_application(request: MazureRequest) -> ResponseType:
    app_object_id = request.path.split("/")[-1]

    app = graph_backend.get_application(app_object_id)
    if app is None:
        return 404, {}, b"Application not found"

    chunk_headers = {
        "Transfer-Encoding": "chunked",
        "Content-Type": "application/json;odata.metadata=minimal;odata.streaming=true;IEEE754Compatible=false;charset=utf-8",
    }
    chunked = chunk_body(json.dumps(app.to_json()).encode("utf-8"))
    return 200, chunk_headers, chunked


@register(
    parent=PathGraph,
    path=r"/v1.0/applications\(appId='[-a-z0-9A-Z]+'\)$",
    method="GET",
)
def get_application_by_app_id(request: MazureRequest) -> ResponseType:
    app_id = re.search("appId='([-a-z0-9A-Z]+)'", request.path).group(1)  # type: ignore

    app = graph_backend.get_application_by_app_id(app_id)
    if app is None:
        return 404, {}, b"Application not found"

    chunk_headers = {
        "Transfer-Encoding": "chunked",
        "Content-Type": "application/json;odata.metadata=minimal;odata.streaming=true;IEEE754Compatible=false;charset=utf-8",
    }
    chunked = chunk_body(json.dumps(app.to_json()).encode("utf-8"))
    return 200, chunk_headers, chunked


@register(
    parent=PathGraph,
    path=r"/v1.0/applications/[-a-z0-9A-Z]+$",
    method="PATCH",
)
def update_application(request: MazureRequest) -> ResponseType:
    app_object_id = request.path.split("/")[-1]

    deeds = json.loads(request.body.decode("utf-8"))
    app = graph_backend.update_application(app_object_id, deeds)
    if app is None:
        return 404, {}, b"Application not found"

    return 204, {}, b""


@register(
    parent=PathGraph,
    path=r"/v1.0/applications\(appId='[-a-z0-9A-Z]+'\)$",
    method="PATCH",
)
def update_application_by_app_id(request: MazureRequest) -> ResponseType:
    app_id = re.search("appId='([-a-z0-9A-Z]+)'", request.path).group(1)  # type: ignore

    deeds = json.loads(request.body.decode("utf-8"))
    app = graph_backend.update_application_by_app_id(app_id, deeds)
    if app is None:
        return 404, {}, b"Application not found"

    return 204, {}, b""


@register(
    parent=PathGraph,
    path=r"/v1.0/applications/[-a-z0-9A-Z]+$",
    method="DELETE",
)
def delete_application(request: MazureRequest) -> ResponseType:
    app_object_id = request.path.split("/")[-1]

    graph_backend.delete_application(app_object_id=app_object_id)

    return 204, {}, b""


@register(
    parent=PathGraph,
    path=r"/v1.0/applications\(appId='[-a-z0-9A-Z]+'\)$",
    method="DELETE",
)
def delete_application_by_app_id(request: MazureRequest) -> ResponseType:
    app_id = re.search("appId='([-a-z0-9A-Z]+)'", request.path).group(1)  # type: ignore

    graph_backend.delete_application(app_id=app_id)

    return 204, {}, b""


@register(
    parent=PathGraph,
    path=r"/directory/deleteditems/microsoft.graph.application$",
    method="GET",
)
def list_deleted_applications(
    request: MazureRequest,  # pylint: disable=unused-argument
) -> ResponseType:
    chunk_headers = {
        "Transfer-Encoding": "chunked",
        "Content-Type": "application/json;odata.metadata=minimal;odata.streaming=true;IEEE754Compatible=false;charset=utf-8",
    }
    app_list = {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#applications",
        "value": [app.to_json() for app in graph_backend.list_deleted_applications()],
    }
    chunked = chunk_body(json.dumps(app_list).encode("utf-8"))

    return 200, chunk_headers, chunked


@register(
    parent=PathGraph,
    path=r"/v1.0/applications/[-a-z0-9A-Z]+/addPassword$",
    method="POST",
)
def add_password(
    request: MazureRequest,  # pylint: disable=unused-argument
) -> ResponseType:
    cred = json.loads(request.body.decode("utf-8"))["passwordCredential"]
    name = cred["displayName"]
    start_time = cred["startDateTime"]
    end_time = cred["endDateTime"]

    key_id = str(uuid4())
    secret = "".join(random.choices(string.digits + string.ascii_letters + "~", k=40))

    cred_response = {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#microsoft.graph.passwordCredential",
        "customKeyIdentifier": None,
        "displayName": name,
        "endDateTime": end_time,
        "hint": "su4",
        "keyId": key_id,
        "secretText": secret,
        "startDateTime": start_time,
    }
    chunk_headers = {
        "Transfer-Encoding": "chunked",
        "Content-Type": "application/json;odata.metadata=minimal;odata.streaming=true;IEEE754Compatible=false;charset=utf-8",
    }
    chunked = chunk_body(json.dumps(cred_response).encode("utf-8"))
    return 200, chunk_headers, chunked


@register(
    parent=PathGraph,
    path=r"/v1.0/servicePrincipals$",
    method="POST",
)
def create_service_principal(
    request: MazureRequest,  # pylint: disable=unused-argument
) -> ResponseType:
    body = json.loads(request.body.decode("utf-8"))
    app_id = body["appId"]
    account_enabled = body["accountEnabled"]

    sp_id = str(uuid4())
    sp_name = str(uuid4())
    app_owner_org_id = str(uuid4())
    name = "TODO"

    service_principal_response = {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#servicePrincipals/$entity",
        "id": sp_id,
        "deletedDateTime": None,
        "accountEnabled": account_enabled,
        "alternativeNames": [],
        "appDisplayName": name,
        "appDescription": None,
        "appId": app_id,
        "applicationTemplateId": None,
        "appOwnerOrganizationId": app_owner_org_id,
        "appRoleAssignmentRequired": False,
        "createdDateTime": None,
        "description": None,
        "disabledByMicrosoftStatus": None,
        "displayName": name,
        "homepage": None,
        "loginUrl": None,
        "logoutUrl": None,
        "notes": None,
        "notificationEmailAddresses": [],
        "preferredSingleSignOnMode": None,
        "preferredTokenSigningKeyThumbprint": None,
        "replyUrls": [],
        "servicePrincipalNames": [sp_name],
        "servicePrincipalType": "Application",
        "signInAudience": "AzureADandPersonalMicrosoftAccount",
        "tags": [],
        "tokenEncryptionKeyId": None,
        "samlSingleSignOnSettings": None,
        "addIns": [],
        "appRoles": [],
        "info": {
            "logoUrl": None,
            "marketingUrl": None,
            "privacyStatementUrl": None,
            "supportUrl": None,
            "termsOfServiceUrl": None,
        },
        "keyCredentials": [],
        "oauth2PermissionScopes": [],
        "passwordCredentials": [],
        "resourceSpecificApplicationPermissions": [],
        "verifiedPublisher": {
            "displayName": None,
            "verifiedPublisherId": None,
            "addedDateTime": None,
        },
    }
    chunk_headers = {
        "Transfer-Encoding": "chunked",
        "Content-Type": "application/json;odata.metadata=minimal;odata.streaming=true;IEEE754Compatible=false;charset=utf-8",
    }
    chunked = chunk_body(json.dumps(service_principal_response).encode("utf-8"))
    return 200, chunk_headers, chunked
