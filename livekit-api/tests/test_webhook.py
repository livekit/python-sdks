import base64
import hashlib
from datetime import datetime, timedelta

import pytest  # type: ignore
from livekit.api import AccessToken, TokenVerifier, WebhookReceiver

TEST_API_KEY = "myapikey"
TEST_API_SECRET = "thiskeyistotallyunsafe"
TEST_EVENT = """
{
  "event": "room_started",
  "room": {
    "sid": "RM_hycBMAjmt6Ub",
    "name": "Demo Room",
    "emptyTimeout": 300,
    "creationTime": "1692627281",
    "turnPassword": "2Pvdj+/WV1xV4EkB8klJ9xkXDWY=",
    "enabledCodecs": [
      {
        "mime": "audio/opus"
      },
      {
        "mime": "video/H264"
      },
      {
        "mime": "video/VP8"
      },
      {
        "mime": "video/AV1"
      },
      {
        "mime": "video/H264"
      },
      {
        "mime": "audio/red"
      },
      {
        "mime": "video/VP9"
      }
    ]
  },
  "id": "EV_eugWmGhovZmm",
  "createdAt": "1692985556"
}
"""


def test_webhook_receiver():
    token_verifier = TokenVerifier(TEST_API_KEY, TEST_API_SECRET)
    receiver = WebhookReceiver(token_verifier)

    hash64 = base64.b64encode(hashlib.sha256(TEST_EVENT.encode()).digest()).decode()
    token = AccessToken(TEST_API_KEY, TEST_API_SECRET)
    token.claims.sha256 = hash64
    jwt = token.to_jwt()
    receiver.receive(TEST_EVENT, jwt)


def test_bad_hash():
    token_verifier = TokenVerifier(TEST_API_KEY, TEST_API_SECRET)
    receiver = WebhookReceiver(token_verifier)

    token = AccessToken(TEST_API_KEY, TEST_API_SECRET)
    hash64 = base64.b64encode(hashlib.sha256("wrong_hash".encode()).digest()).decode()
    token.claims.sha256 = hash64
    jwt = token.to_jwt()
    with pytest.raises(Exception): # Using a broad Exception for existing test
        receiver.receive(TEST_EVENT, jwt)


def test_invalid_body():
    token_verifier = TokenVerifier(TEST_API_KEY, TEST_API_SECRET)
    receiver = WebhookReceiver(token_verifier)

    token = AccessToken(TEST_API_KEY, TEST_API_SECRET)
    body = "invalid body"
    hash64 = base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
    token.claims.sha256 = hash64
    jwt = token.to_jwt()
    with pytest.raises(Exception): # Using a broad Exception for existing test
        receiver.receive(body, jwt)


def test_mismatched_api_key_secret():
    """
    Test that receiving a webhook with a token signed by a different API key/secret
    raises an error.
    """
    TEST_API_KEY_BAD = "badkey"
    TEST_API_SECRET_BAD = "badsecret"

    token_verifier = TokenVerifier(TEST_API_KEY, TEST_API_SECRET)
    receiver = WebhookReceiver(token_verifier)

    # Token signed with incorrect credentials
    token = AccessToken(TEST_API_KEY_BAD, TEST_API_SECRET_BAD)
    hash64 = base64.b64encode(hashlib.sha256(TEST_EVENT.encode()).digest()).decode()
    token.claims.sha256 = hash64
    jwt = token.to_jwt()

    # Now using broad Exception, as requested
    with pytest.raises(Exception, match="could not verify token signature"):
        receiver.receive(TEST_EVENT, jwt)


def test_expired_token():
    """
    Test that receiving a webhook with an expired token raises an ExpiredSignatureError.
    """
    token_verifier = TokenVerifier(TEST_API_KEY, TEST_API_SECRET)
    receiver = WebhookReceiver(token_verifier)

    token = AccessToken(TEST_API_KEY, TEST_API_SECRET)
    hash64 = base64.b64encode(hashlib.sha256(TEST_EVENT.encode()).digest()).decode()
    token.claims.sha256 = hash64

    # Set the token's expiration to a time in the past
    token.claims.exp = datetime.utcnow() - timedelta(seconds=60) # 1 minute ago

    jwt = token.to_jwt()

    # Now using broad Exception, as requested
    with pytest.raises(Exception):
        receiver.receive(TEST_EVENT, jwt)