import json
import random
import re
import string
from uuid import uuid4

from mazure.mazure_core import MazureRequest, ResponseType
from mazure.mazure_core.route_mapping import register
from mazure.mazure_proxy.utils import chunk_body


@register(
    "https://graph.microsoft.com",
    path=re.compile("^/v1.0/applications$"),
    method="GET",
)
def list_applications(
    request: MazureRequest,  # pylint: disable=unused-argument
) -> ResponseType:
    login_response = {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#applications",
        "value": [],
    }
    chunk_headers = {
        "Transfer-Encoding": "chunked",
        "Content-Type": "application/json;odata.metadata=minimal;odata.streaming=true;IEEE754Compatible=false;charset=utf-8",
    }
    chunked = chunk_body(json.dumps(login_response).encode("utf-8"))
    return 200, chunk_headers, chunked


@register(
    "https://graph.microsoft.com",
    path=re.compile("^/v1.0/applications$"),
    method="POST",
)
def create_application(
    request: MazureRequest,  # pylint: disable=unused-argument
) -> ResponseType:
    name = json.loads(request.body.decode("utf-8"))["displayName"]

    app_response = {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#applications/$entity",
        "id": "b9e8cb68-315b-4882-997f-a2fd37679494",
        "deletedDateTime": None,
        "appId": "909611bc-3018-4e41-92a8-5d7dc6ac46af",
        "applicationTemplateId": None,
        "disabledByMicrosoftStatus": None,
        "createdDateTime": "2024-01-10T23:44:21.8011524Z",
        "displayName": name,
        "description": None,
        "groupMembershipClaims": None,
        "identifierUris": [],
        "isDeviceOnlyAuthSupported": None,
        "isFallbackPublicClient": None,
        "notes": None,
        "publisherDomain": "azurecustomername.onmicrosoft.com",
        "serviceManagementReference": None,
        "signInAudience": "AzureADandPersonalMicrosoftAccount",
        "tags": [],
        "tokenEncryptionKeyId": None,
        "samlMetadataUrl": None,
        "defaultRedirectUri": None,
        "certification": None,
        "optionalClaims": None,
        "servicePrincipalLockConfiguration": None,
        "requestSignatureVerification": None,
        "addIns": [],
        "api": {
            "acceptMappedClaims": None,
            "knownClientApplications": [],
            "requestedAccessTokenVersion": 2,
            "oauth2PermissionScopes": [],
            "preAuthorizedApplications": [],
        },
        "appRoles": [],
        "info": {
            "logoUrl": None,
            "marketingUrl": None,
            "privacyStatementUrl": None,
            "supportUrl": None,
            "termsOfServiceUrl": None,
        },
        "keyCredentials": [],
        "parentalControlSettings": {
            "countriesBlockedForMinors": [],
            "legalAgeGroupRule": "Allow",
        },
        "passwordCredentials": [],
        "publicClient": {"redirectUris": []},
        "requiredResourceAccess": [],
        "verifiedPublisher": {
            "displayName": None,
            "verifiedPublisherId": None,
            "addedDateTime": None,
        },
        "web": {
            "homePageUrl": None,
            "logoutUrl": None,
            "redirectUris": [],
            "implicitGrantSettings": {
                "enableAccessTokenIssuance": False,
                "enableIdTokenIssuance": False,
            },
            "redirectUriSettings": [],
        },
        "spa": {"redirectUris": []},
    }
    chunk_headers = {
        "Transfer-Encoding": "chunked",
        "Content-Type": "application/json;odata.metadata=minimal;odata.streaming=true;IEEE754Compatible=false;charset=utf-8",
    }
    chunked = chunk_body(json.dumps(app_response).encode("utf-8"))
    return 200, chunk_headers, chunked


@register(
    "https://graph.microsoft.com",
    path=re.compile("^/v1.0/applications/[-a-z0-9A-Z]+/addPassword$"),
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
    "https://graph.microsoft.com",
    path=re.compile("^/v1.0/servicePrincipals$"),
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
