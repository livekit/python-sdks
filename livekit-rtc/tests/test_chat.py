from datetime import datetime
import json

from livekit.rtc import ChatMessage


def test_message_basics():
    msg = ChatMessage()
    assert msg.id is not None, "message id should be set"
    assert msg.timestamp is not None, "timestamp should be set"
    assert msg.timestamp.day == datetime.now().day, "timestamp should be today"
    assert len(msg.id) > 5, "message id should be long enough"


def test_message_serialization():
    msg = ChatMessage(
        message="hello",
    )
    data = msg.asjsondict()
    msg2 = ChatMessage.from_jsondict(json.loads(json.dumps(data)))
    assert msg2.message == msg.message, "message should be the same"
    assert msg2.id == msg.id, "id should be the same"
    assert int(msg2.timestamp.timestamp() / 1000) == int(
        msg.timestamp.timestamp() / 1000
    ), "timestamp should be the same"
    assert not msg2.deleted, "not deleted"

    # deletion is handled
    msg.deleted = True
    data = msg.asjsondict()
    msg2 = ChatMessage.from_jsondict(json.loads(json.dumps(data)))
    assert msg2.deleted, "should be deleted"
