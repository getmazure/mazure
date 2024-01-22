from peewee import Model, TextField


class StorageContainer(Model):  # type: ignore[misc]
    name = TextField(primary_key=True)

    def to_xml(self) -> str:
        return (
            "<Container>"
            f"<Name>{self.name}</Name>"
            "<Properties>"
            "<Last-Modified>Sun, 21 Jan 2024 12:25:40 GMT</Last-Modified>"
            f'<Etag>"{hex(hash(self.name))}"</Etag>'
            "<LeaseStatus>unlocked</LeaseStatus>"
            "<LeaseState>available</LeaseState>"
            "<DefaultEncryptionScope>$account-encryption-key</DefaultEncryptionScope>"
            "<DenyEncryptionScopeOverride>false</DenyEncryptionScopeOverride>"
            "<HasImmutabilityPolicy>false</HasImmutabilityPolicy>"
            "<HasLegalHold>false</HasLegalHold>"
            "<ImmutableStorageWithVersioningEnabled>false</ImmutableStorageWithVersioningEnabled>"
            "</Properties>"
            "</Container>"
        )
