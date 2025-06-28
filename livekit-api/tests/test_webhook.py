import base64
import hashlib

import pytest  # type: ignore
from livekit.api import AccessToken, TokenVerifier, WebhookReceiver
from livekit.protocol.webhook import WebhookEvent # Keep this line
from livekit.protocol.models import ( # Added this import
    Room,
    ParticipantInfo,
    TrackInfo,
    TrackKind,
    TrackSource,
)

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


# --- ADDITIONAL TESTS START HERE ---

# New test event: participant_connected
TEST_EVENT_PARTICIPANT_CONNECTED = """
{
  "event": "participant_connected",
  "room": {
    "sid": "RM_hycBMAjmt6Ub",
    "name": "Demo Room",
    "emptyTimeout": 300,
    "creationTime": "1692627281",
    "numParticipants": 2
  },
  "participant": {
    "sid": "PA_abcdefg",
    "identity": "user123",
    "state": 1,
    "joinedAt": "1692985600",
    "name": "User 1"
  },
  "id": "EV_participant_connected_test",
  "createdAt": "1692985600"
}
"""

# New test event: track_published
TEST_EVENT_TRACK_PUBLISHED = """
{
  "event": "track_published",
  "room": {
    "sid": "RM_hycBMAjmt6Ub",
    "name": "Demo Room"
  },
  "participant": {
    "sid": "PA_abcdefg",
    "identity": "user123",
    "state": 2
  },
  "track": {
    "sid": "TR_hijklm",
    "name": "camera",
    "kind": "VIDEO",
    "source": "CAMERA",
    "width": 640,
    "height": 480,
    "muted": false
  },
  "id": "EV_track_published_test",
  "createdAt": "1692985700"
}
"""

# New test event: room_ended
TEST_EVENT_ROOM_ENDED = """
{
  "event": "room_ended",
  "room": {
    "sid": "RM_hycBMAjmt6Ub",
    "name": "Demo Room",
    "emptyTimeout": 300,
    "creationTime": "1692627281",
    "numParticipants": 0
  },
  "id": "EV_room_ended_test",
  "createdAt": "1692986000"
}
"""


def generate_webhook_token(event_body: str) -> str:
    """Helper to generate a valid webhook token for a given event body."""
    hash64 = base64.b64encode(hashlib.sha256(event_body.encode()).digest()).decode()
    token = AccessToken(TEST_API_KEY, TEST_API_SECRET)
    token.claims.sha256 = hash64
    return token.to_jwt()


def test_webhook_receiver_room_started_details():
    """Test successful reception of a room_started event with content verification."""
    token_verifier = TokenVerifier(TEST_API_KEY, TEST_API_SECRET)
    receiver = WebhookReceiver(token_verifier)

    jwt = generate_webhook_token(TEST_EVENT) # Using original TEST_EVENT here
    event = receiver.receive(TEST_EVENT, jwt)

    assert event.event == "room_started"
    assert event.room.sid == "RM_hycBMAjmt6Ub"
    assert event.room.name == "Demo Room"
    assert event.room.empty_timeout == 300
    assert event.room.creation_time == 1692627281 # Proto message parses as int
    assert len(event.room.enabled_codecs) > 0


def test_webhook_receiver_participant_connected_details():
    """Test successful reception of a participant_connected event with content verification."""
    token_verifier = TokenVerifier(TEST_API_KEY, TEST_API_SECRET)
    receiver = WebhookReceiver(token_verifier)

    jwt = generate_webhook_token(TEST_EVENT_PARTICIPANT_CONNECTED)
    event = receiver.receive(TEST_EVENT_PARTICIPANT_CONNECTED, jwt)

    assert event.event == "participant_connected"
    assert isinstance(event.participant, ParticipantInfo)
    assert event.participant.identity == "user123"
    assert event.participant.sid == "PA_abcdefg"
    assert event.participant.name == "User 1"
    assert event.room.sid == "RM_hycBMAjmt6Ub"
    assert event.room.num_participants == 2


def test_webhook_receiver_track_published_details():
    """Test successful reception of a track_published event with content verification."""
    token_verifier = TokenVerifier(TEST_API_KEY, TEST_API_SECRET)
    receiver = WebhookReceiver(token_verifier)

    jwt = generate_webhook_token(TEST_EVENT_TRACK_PUBLISHED)
    event = receiver.receive(TEST_EVENT_TRACK_PUBLISHED, jwt)

    assert event.event == "track_published"
    assert isinstance(event.track, TrackInfo)
    assert event.track.sid == "TR_hijklm"
    assert event.track.name == "camera"
    assert event.track.kind == TrackKind.KIND_VIDEO
    assert event.track.source == TrackSource.CAMERA
    assert event.track.width == 640
    assert event.track.height == 480
    assert not event.track.muted
    assert event.participant.identity == "user123"


def test_webhook_receiver_room_ended_details():
    """Test successful reception of a room_ended event with content verification."""
    token_verifier = TokenVerifier(TEST_API_KEY, TEST_API_SECRET)
    receiver = WebhookReceiver(token_verifier)

    jwt = generate_webhook_token(TEST_EVENT_ROOM_ENDED)
    event = receiver.receive(TEST_EVENT_ROOM_ENDED, jwt)

    assert event.event == "room_ended"
    assert event.room.sid == "RM_hycBMAjmt6Ub"
    assert event.room.name == "Demo Room"
    assert event.room.num_participants == 0


def test_missing_sha256_claim_raises_error():
    """Test that missing SHA256 in the token claims raises an exception."""
    token_verifier = TokenVerifier(TEST_API_KEY, TEST_API_SECRET)
    receiver = WebhookReceiver(token_verifier)

    # Create a token without explicitly setting claims.sha256
    token_without_sha256 = AccessToken(TEST_API_KEY, TEST_API_SECRET).to_jwt()

    with pytest.raises(Exception, match="sha256 was not found in the token"):
        receiver.receive(TEST_EVENT, token_without_sha256)