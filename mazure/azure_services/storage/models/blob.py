from peewee import BlobField, Model, TextField


class Blob(Model):  # type: ignore[misc]
    name = TextField(primary_key=True)
    content = BlobField()
    content_type = TextField(null=True)

    def to_xml(self) -> str:
        return (
            "<Blob>"
            f"<Name>{self.name}</Name>"
            "<Properties>"
            "<Creation-Time>Sun, 21 Jan 2024 12:26:48 GMT</Creation-Time>"
            "<Last-Modified>Sun, 21 Jan 2024 12:26:48 GMT</Last-Modified>"
            "<Etag>0x8DC1A7C3CF7ED3F</Etag>"
            f"<Content-Length>{str(len(self.content))}</Content-Length>"
            f"<Content-Type>{self.content_type}</Content-Type>"
            "<Content-Encoding />"
            "<Content-Language />"
            "<Content-CRC64 />"
            "<Content-MD5>Fz1QNVkIouIfL+S61EjOVw==</Content-MD5>"
            "<Cache-Control />"
            "<Content-Disposition />"
            "<BlobType>BlockBlob</BlobType>"
            "<AccessTier>Hot</AccessTier>"
            "<AccessTierInferred>true</AccessTierInferred>"
            "<LeaseStatus>unlocked</LeaseStatus>"
            "<LeaseState>available</LeaseState>"
            "<ServerEncrypted>true</ServerEncrypted>"
            "</Properties>"
            "<OrMetadata />"
            "</Blob>"
        )
