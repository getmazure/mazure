import base64
import json
import random
import string
from datetime import datetime, timezone
from urllib.parse import unquote

import jwt

from mazure.mazure_core import ResponseType
from mazure.mazure_core.mazure_request import MazureRequest
from mazure.mazure_core.route_mapping import register, register_parent


@register_parent(path="https://login.microsoftonline.com")
class MicrosoftLogin:
    pass


@register_parent(path="http://169.254.169.254")
class ManagedIdentityServer:
    pass


@register(
    parent=MicrosoftLogin,
    path=r"/[-a-z0-9A-Z]+/.well-known/openid-configuration$",
    method="GET",
)
def get_wellknown_endpoint(request: MazureRequest) -> ResponseType:
    return get_wellknown_endpoint_2(request)


@register(
    parent=MicrosoftLogin,
    path=r"/[-a-z0-9A-Z]+/v2.0/.well-known/openid-configuration$",
    method="GET",
)
def get_wellknown_endpoint_2(
    request: MazureRequest,  # pylint: disable=unused-argument
) -> ResponseType:
    sub_id = request.path.split("/")[1]

    wellknown_response = {
        "authorization_endpoint": f"https://login.microsoftonline.com/{sub_id}/oauth2/v2.0/authorize",
        "claims_supported": [
            "sub",
            "iss",
            "cloud_instance_name",
            "cloud_instance_host_name",
            "cloud_graph_host_name",
            "msgraph_host",
            "aud",
            "exp",
            "iat",
            "auth_time",
            "acr",
            "nonce",
            "preferred_username",
            "name",
            "tid",
            "ver",
            "at_hash",
            "c_hash",
            "email",
        ],
        "cloud_graph_host_name": "graph.windows.net",
        "cloud_instance_name": "microsoftonline.com",
        "device_authorization_endpoint": f"https://login.microsoftonline.com/{sub_id}/oauth2/v2.0/devicecode",
        "end_session_endpoint": f"https://login.microsoftonline.com/{sub_id}/oauth2/v2.0/logout",
        "frontchannel_logout_supported": True,
        "http_logout_supported": True,
        "id_token_signing_alg_values_supported": ["RS256"],
        "issuer": f"https://login.microsoftonline.com/{sub_id}/v2.0",
        "jwks_uri": f"https://login.microsoftonline.com/{sub_id}/discovery/v2.0/keys",
        "kerberos_endpoint": f"https://login.microsoftonline.com/{sub_id}/kerberos",
        "msgraph_host": "graph.microsoft.com",
        "rbac_url": "https://pas.windows.net",
        "request_uri_parameter_supported": False,
        "response_modes_supported": ["query", "fragment", "form_post"],
        "response_types_supported": [
            "code",
            "id_token",
            "code id_token",
            "id_token token",
        ],
        "scopes_supported": ["openid", "profile", "email", "offline_access"],
        "subject_types_supported": ["pairwise"],
        "tenant_region_scope": "EU",
        "token_endpoint": f"https://login.microsoftonline.com/{sub_id}/oauth2/v2.0/token",
        "token_endpoint_auth_methods_supported": [
            "client_secret_post",
            "private_key_jwt",
            "client_secret_basic",
        ],
        "userinfo_endpoint": "https://graph.microsoft.com/oidc/userinfo",
    }

    return 200, {}, json.dumps(wellknown_response).encode("utf-8")


@register(
    parent=MicrosoftLogin,
    path=r"/[-a-z0-9A-Z]+/oauth2/v2.0/token$",
    method="POST",
)
def get_oauth_token(
    request: MazureRequest,  # pylint: disable=unused-argument
) -> ResponseType:
    sub_id = request.path.split("/")[1]
    access_token = "".join(
        random.choices(string.digits + string.ascii_letters + "_-.", k=2404)
    )
    refresh_token = "".join(
        random.choices(
            string.digits + string.ascii_letters + string.digits + "_-.", k=1608
        )
    )

    mailbox = request.headers.get("X-AnchorMailbox")
    if mailbox:
        if mailbox.startswith("0id:"):
            mailbox = mailbox[4:]
        uid, utid = mailbox.split("@")
        raw_info = json.dumps({"uid": uid, "utid": utid}).encode("utf-8")
        client_info = base64.b64encode(raw_info)
    else:
        client_info = None

    params = request.body.decode("utf-8").split("&")
    client_id = [p.split("=")[1] for p in params if p.startswith("client_id=")]

    id_token = jwt.encode(
        payload={
            "iss": f"https://login.microsoftonline.com/{sub_id}/v2.0",
            "aud": client_id,
            "exp": datetime.now(tz=timezone.utc),
            "sub": "some data",
            "preferred_username": "My Name",
            "upn": "My Name",
            "tid": sub_id,
        },
        key="secret",
        algorithm="HS256",
        headers={"kid": "5B3nRxtQ7ji8eNDc3Fy05Kf97ZE"},
    )
    login_response = {
        "token_type": "Bearer",
        "scope": "email openid profile https://graph.microsoft.com//AuditLog.Read.All https://graph.microsoft.com//Directory.AccessAsUser.All https://graph.microsoft.com//Group.ReadWrite.All https://graph.microsoft.com//User.ReadWrite.All https://graph.microsoft.com//.default",
        "expires_in": 4922,
        "ext_expires_in": 4922,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "foci": "1",
        "id_token": id_token,
    }
    if client_info is not None:
        login_response["client_info"] = client_info.decode("utf-8")
    return 200, {}, json.dumps(login_response).encode("utf-8")


@register(
    parent=ManagedIdentityServer,
    path=r"/metadata/identity/oauth2/token$",
    method="GET",
)
def get_oauth_token__managed_identity(
    request: MazureRequest,  # pylint: disable=unused-argument
) -> ResponseType:
    refresh_token = ""

    resource = [
        unquote(a.split("=")[-1])
        for a in request.parsed_path.query.split("&")
        if a.startswith("resource=")
    ][0]

    delta = datetime.utcnow() - datetime.utcfromtimestamp(0)
    not_before = int(
        (delta.days * 86400) + (delta.seconds + (delta.microseconds / 1e6)) - 5000
    )
    expires_on = int(
        (delta.days * 86400) + (delta.seconds + (delta.microseconds / 1e6)) + 5000
    )
    access_token = jwt.encode(
        payload={
            "iss": resource,
            "exp": expires_on,
            "nbf": not_before,
            "iat": datetime.utcnow(),
        },
        key="secret",
        algorithm="HS256",
        headers={"kid": "5B3nRxtQ7ji8eNDc3Fy05Kf97ZE"},
    )
    login_response = {
        "token_type": "Bearer",
        "expires_in": 4922,
        "expires_on": expires_on,
        "not_before": not_before,
        "resource": resource,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    return 200, {}, json.dumps(login_response).encode("utf-8")
