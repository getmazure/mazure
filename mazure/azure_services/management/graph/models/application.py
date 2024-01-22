from typing import Any, Dict
from uuid import uuid4

from peewee import Model, TextField, UUIDField


class Application(Model):  # type: ignore[misc]
    app_object_id = UUIDField(primary_key=True, default=uuid4)
    app_id = UUIDField(default=uuid4)
    name = TextField()

    def update_details(self, body: Dict[str, Any]) -> None:
        if "displayName" in body:
            self.name = body["displayName"]
        self.save()

    def to_json(self) -> Dict[str, Any]:
        return {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#applications/$entity",
            "id": str(self.app_object_id),
            "deletedDateTime": None,
            "appId": str(self.app_id),
            "applicationTemplateId": None,
            "disabledByMicrosoftStatus": None,
            "createdDateTime": "2024-01-10T23:44:21.8011524Z",
            "displayName": self.name,
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


class DeletedApplication(Application):
    pass
