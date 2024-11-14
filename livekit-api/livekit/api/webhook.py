from .access_token import TokenVerifier
from livekit.protocol.webhook import WebhookEvent
from google.protobuf.json_format import Parse
import hashlib
import base64


class WebhookReceiver:
    def __init__(self, token_verifier: TokenVerifier):
        self._verifier = token_verifier

    def receive(self, body: str, auth_token: str) -> WebhookEvent:
        claims = self._verifier.verify(auth_token)
        if claims.sha256 is None:
            raise Exception("sha256 was not found in the token")

        body_hash = hashlib.sha256(body.encode()).digest()
        claims_hash = base64.b64decode(claims.sha256)

        if body_hash != claims_hash:
            raise Exception("hash mismatch")

        return Parse(body, WebhookEvent(), ignore_unknown_fields=True)
