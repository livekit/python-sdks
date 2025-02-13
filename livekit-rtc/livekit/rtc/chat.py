# Copyright 2023 LiveKit, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
from typing import Any, Dict, Literal, Optional
import asyncio

from .room import Room, Participant, DataPacket, TextStreamReader, RemoteParticipant, LocalParticipant
from .event_emitter import EventEmitter
from ._utils import generate_random_base62

_LEGACY_CHAT_TOPIC = "lk-chat-topic"
_LEGACY_CHAT_UPDATE_TOPIC = "lk-chat-update-topic"
_DS_CHAT_TOPIC = "lk.chat"

EventTypes = Literal["message_received",]


class ChatManager(EventEmitter[EventTypes]):
    """A utility class that sends and receives chat messages in the active session.

    It implements LiveKit Chat Protocol, and serializes data to/from JSON data packets.
    """

    def __init__(self, room: Room):
        super().__init__()
        self._lp = room.local_participant
        self._room = room
        self._tasks: list[asyncio.Task] = []

        room.on("data_received", self._on_data_received)
        room.unregister_text_stream_handler(_DS_CHAT_TOPIC)
        room.register_text_stream_handler(_DS_CHAT_TOPIC, self._on_text_stream_received)

    def close(self):
        self._room.off("data_received", self._on_data_received)
        self._room.unregister_text_stream_handler(_DS_CHAT_TOPIC)
        for task in self._tasks:
            task.cancel()

    async def send_message(self, message: str) -> "ChatMessage":
        """Send a chat message to the end user using LiveKit Chat Protocol.

        Args:
            message (str): the message to send

        Returns:
            ChatMessage: the message that was sent
        """
        msg = ChatMessage(
            message=message,
            is_local=True,
            participant=self._lp,
        )
        msg_dict = msg.asjsondict()
        msg_dict["ignoreLegacy"] = True
        await self._lp.send_text(message, topic=_DS_CHAT_TOPIC)
        await self._lp.publish_data(
            payload=json.dumps(msg_dict),
            topic=_LEGACY_CHAT_TOPIC,
        )
        return msg

    async def update_message(self, message: "ChatMessage"):
        """Update a chat message that was previously sent.

        If message.deleted is set to True, we'll signal to remote participants that the message
        should be deleted.
        """
        await self._lp.publish_data(
            payload=json.dumps(message.asjsondict()),
            topic=_LEGACY_CHAT_UPDATE_TOPIC,
        )

    def _on_data_received(self, dp: DataPacket):
        # handle both new and updates the same way, as long as the ID is in there
        # the user can decide how to replace the previous message
        if dp.topic == _LEGACY_CHAT_TOPIC or dp.topic == _LEGACY_CHAT_UPDATE_TOPIC:
            try:
                parsed = json.loads(dp.data)
                # if the message is marked as ignoreLegacy, we'll skip it
                if parsed.get("ignoreLegacy"):
                    return
                msg = ChatMessage.from_jsondict(parsed)
                if dp.participant:
                    msg.participant = dp.participant
                self.emit("message_received", msg)
            except Exception as e:
                logging.warning("failed to parse chat message: %s", e, exc_info=e)
    
    def _on_text_stream_received(self, stream: TextStreamReader, participant_identity: str):
        task = asyncio.create_task(self._handle_text_stream(stream, participant_identity))
        self._tasks.append(task)
        task.add_done_callback(self._tasks.remove)

    async def _handle_text_stream(self, stream: TextStreamReader, participant_identity: str):
        msg = await ChatMessage.from_text_stream(stream)
        participant: RemoteParticipant | LocalParticipant | None = self._room._remote_participants.get(participant_identity)
        if participant is None and self._room.local_participant.identity == participant_identity:
            participant = self._room.local_participant
            msg.is_local = True
        msg.participant = participant
        self.emit("message_received", msg)


@dataclass
class ChatMessage:
    message: Optional[str] = None
    id: str = field(default_factory=generate_random_base62)
    timestamp: datetime = field(default_factory=datetime.now)
    deleted: bool = field(default=False)

    # These fields are not part of the wire protocol. They are here to provide
    # context for the application.
    participant: Optional[Participant] = None
    is_local: bool = field(default=False)

    @classmethod
    def from_jsondict(cls, d: Dict[str, Any]) -> "ChatMessage":
        # older version of the protocol didn't contain a message ID, so we'll create one
        id = d.get("id") or generate_random_base62()
        timestamp = datetime.now()
        if d.get("timestamp"):
            timestamp = datetime.fromtimestamp(d.get("timestamp", 0) / 1000.0)
        msg = cls(
            id=id,
            timestamp=timestamp,
        )
        msg.update_from_jsondict(d)
        return msg

    def update_from_jsondict(self, d: Dict[str, Any]) -> None:
        self.message = d.get("message")
        self.deleted = d.get("deleted", False)

    def asjsondict(self):
        """Returns a JSON serializable dictionary representation of the message."""
        d = {
            "id": self.id,
            "message": self.message,
            "timestamp": int(self.timestamp.timestamp() * 1000),
        }
        if self.deleted:
            d["deleted"] = True
        return d
    
    @classmethod
    async def from_text_stream(cls, stream: TextStreamReader):
        message_text = await stream.read_all()
        timestamp = datetime.fromtimestamp(stream.info.timestamp / 1000.0)
        return cls(
            message=message_text, 
            timestamp=timestamp, 
            id=stream.info.stream_id, 
        )
