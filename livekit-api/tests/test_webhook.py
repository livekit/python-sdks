import base64
import hashlib

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
    with pytest.raises(Exception):
        receiver.receive(TEST_EVENT, jwt)


def test_invalid_body():
    token_verifier = TokenVerifier(TEST_API_KEY, TEST_API_SECRET)
    receiver = WebhookReceiver(token_verifier)

    token = AccessToken(TEST_API_KEY, TEST_API_SECRET)
    body = "invalid body"
    hash64 = base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
    token.claims.sha256 = hash64
    jwt = token.to_jwt()
    with pytest.raises(Exception):
        receiver.receive(body, jwt)
