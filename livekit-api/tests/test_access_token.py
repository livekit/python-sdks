import datetime

import pytest  # type: ignore
from livekit.api import AccessToken, TokenVerifier, VideoGrants

TEST_API_KEY = "myapikey"
TEST_API_SECRET = "thiskeyistotallyunsafe"


def test_verify_token():
    grants = VideoGrants(room_join=True, room="test_room")

    token = (
        AccessToken(TEST_API_KEY, TEST_API_SECRET)
        .with_identity("test_identity")
        .with_metadata("test_metadata")
        .with_grants(grants)
        .to_jwt()
    )

    token_verifier = TokenVerifier(TEST_API_KEY, TEST_API_SECRET)
    claims = token_verifier.verify(token)

    assert claims.identity == "test_identity"
    assert claims.metadata == "test_metadata"
    assert claims.video == grants


def test_verify_token_invalid():
    token = (
        AccessToken(TEST_API_KEY, TEST_API_SECRET)
        .with_identity("test_identity")
        .to_jwt()
    )

    token_verifier = TokenVerifier(TEST_API_KEY, "invalid_secret")
    with pytest.raises(Exception):
        token_verifier.verify(token)

    token_verifier = TokenVerifier("invalid_key", TEST_API_SECRET)
    with pytest.raises(Exception):
        token_verifier.verify(token)


def test_verify_token_expired():
    token = (
        AccessToken(TEST_API_KEY, TEST_API_SECRET)
        .with_identity("test_identity")
        .with_ttl(datetime.timedelta(seconds=-1))
        .to_jwt()
    )

    token_verifier = TokenVerifier(
        TEST_API_KEY, TEST_API_SECRET, leeway=datetime.timedelta(seconds=0)
    )
    with pytest.raises(Exception):
        token_verifier.verify(token)
