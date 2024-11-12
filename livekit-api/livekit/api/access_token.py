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

import calendar
import dataclasses
import re
import datetime
import os
import jwt
from typing import Optional, List, Literal
from google.protobuf.json_format import MessageToDict, ParseDict

from livekit.protocol.room import RoomConfiguration

DEFAULT_TTL = datetime.timedelta(hours=6)
DEFAULT_LEEWAY = datetime.timedelta(minutes=1)


@dataclasses.dataclass
class VideoGrants:
    # actions on rooms
    room_create: Optional[bool] = None
    room_list: Optional[bool] = None
    room_record: Optional[bool] = None

    # actions on a particular room
    room_admin: Optional[bool] = None
    room_join: Optional[bool] = None
    room: str = ""

    # permissions within a room
    can_publish: bool = True
    can_subscribe: bool = True
    can_publish_data: bool = True

    # TrackSource types that a participant may publish.
    # When set, it supersedes CanPublish. Only sources explicitly set here can be
    # published
    can_publish_sources: Optional[List[str]] = None

    # by default, a participant is not allowed to update its own metadata
    can_update_own_metadata: Optional[bool] = None

    # actions on ingresses
    ingress_admin: Optional[bool] = None  # applies to all ingress

    # participant is not visible to other participants (useful when making bots)
    hidden: Optional[bool] = None

    # [deprecated] indicates to the room that current participant is a recorder
    recorder: Optional[bool] = None

    # indicates that the holder can register as an Agent framework worker
    agent: Optional[bool] = None


@dataclasses.dataclass
class SIPGrants:
    # manage sip resources
    admin: bool = False
    # make outbound calls
    call: bool = False


@dataclasses.dataclass
class Claims:
    identity: str = ""
    name: str = ""
    kind: str = ""
    metadata: str = ""
    video: Optional[VideoGrants] = None
    sip: Optional[SIPGrants] = None
    attributes: Optional[dict[str, str]] = None
    sha256: Optional[str] = None
    room_preset: Optional[str] = None
    room_config: Optional[RoomConfiguration] = None

    def asdict(self) -> dict:
        # in order to produce minimal JWT size, exclude None or empty values
        claims = dataclasses.asdict(
            self,
            dict_factory=lambda items: {
                snake_to_lower_camel(k): v
                for k, v in items
                if v is not None and v != ""
            },
        )
        if self.room_config:
            claims["roomConfig"] = MessageToDict(self.room_config)
        return claims


class AccessToken:
    ParticipantKind = Literal["standard", "egress", "ingress", "sip", "agent"]

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
    ) -> None:
        api_key = api_key or os.getenv("LIVEKIT_API_KEY")
        api_secret = api_secret or os.getenv("LIVEKIT_API_SECRET")

        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret must be set")

        self.api_key = api_key  # iss
        self.api_secret = api_secret
        self.claims = Claims()

        # default jwt claims
        self.identity = ""  # sub
        self.ttl = DEFAULT_TTL  # exp

    def with_ttl(self, ttl: datetime.timedelta) -> "AccessToken":
        self.ttl = ttl
        return self

    def with_grants(self, grants: VideoGrants) -> "AccessToken":
        self.claims.video = grants
        return self

    def with_sip_grants(self, grants: SIPGrants) -> "AccessToken":
        self.claims.sip = grants
        return self

    def with_identity(self, identity: str) -> "AccessToken":
        self.identity = identity
        return self

    def with_kind(self, kind: ParticipantKind) -> "AccessToken":
        self.claims.kind = kind
        return self

    def with_name(self, name: str) -> "AccessToken":
        self.claims.name = name
        return self

    def with_metadata(self, metadata: str) -> "AccessToken":
        self.claims.metadata = metadata
        return self

    def with_attributes(self, attributes: dict[str, str]) -> "AccessToken":
        self.claims.attributes = attributes
        return self

    def with_sha256(self, sha256: str) -> "AccessToken":
        self.claims.sha256 = sha256
        return self

    def with_room_preset(self, preset: str) -> "AccessToken":
        self.claims.room_preset = preset
        return self

    def with_room_config(self, config: RoomConfiguration) -> "AccessToken":
        self.claims.room_config = config
        return self

    def to_jwt(self) -> str:
        video = self.claims.video
        if video and video.room_join and (not self.identity or not video.room):
            raise ValueError("identity and room must be set when joining a room")

        # we want to exclude None values from the token
        jwt_claims = self.claims.asdict()
        jwt_claims.update(
            {
                "sub": self.identity,
                "iss": self.api_key,
                "nbf": calendar.timegm(
                    datetime.datetime.now(datetime.timezone.utc).utctimetuple()
                ),
                "exp": calendar.timegm(
                    (
                        datetime.datetime.now(datetime.timezone.utc) + self.ttl
                    ).utctimetuple()
                ),
            }
        )
        return jwt.encode(jwt_claims, self.api_secret, algorithm="HS256")


class TokenVerifier:
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        *,
        leeway: datetime.timedelta = DEFAULT_LEEWAY,
    ) -> None:
        api_key = api_key or os.getenv("LIVEKIT_API_KEY")
        api_secret = api_secret or os.getenv("LIVEKIT_API_SECRET")

        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret must be set")

        self.api_key = api_key
        self.api_secret = api_secret
        self._leeway = leeway

    def verify(self, token: str) -> Claims:
        claims = jwt.decode(
            token,
            self.api_secret,
            issuer=self.api_key,
            algorithms=["HS256"],
            leeway=self._leeway.total_seconds(),
        )

        video_dict = claims.get("video", dict())
        video_dict = {camel_to_snake(k): v for k, v in video_dict.items()}
        video_dict = {
            k: v for k, v in video_dict.items() if k in VideoGrants.__dataclass_fields__
        }
        video = VideoGrants(**video_dict)

        sip_dict = claims.get("sip", dict())
        sip_dict = {camel_to_snake(k): v for k, v in sip_dict.items()}
        sip_dict = {
            k: v for k, v in sip_dict.items() if k in SIPGrants.__dataclass_fields__
        }
        sip = SIPGrants(**sip_dict)

        grant_claims = Claims(
            identity=claims.get("sub", ""),
            name=claims.get("name", ""),
            video=video,
            sip=sip,
            attributes=claims.get("attributes", {}),
            metadata=claims.get("metadata", ""),
            sha256=claims.get("sha256", ""),
        )

        if claims.get("roomPreset"):
            grant_claims.room_preset = claims.get("roomPreset")
        if claims.get("roomConfig"):
            grant_claims.room_config = ParseDict(
                claims.get("roomConfig"),
                RoomConfiguration(),
                ignore_unknown_fields=True,
            )

        return grant_claims


def camel_to_snake(t: str):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", t).lower()


def snake_to_lower_camel(t: str):
    return "".join(
        word.capitalize() if i else word for i, word in enumerate(t.split("_"))
    )
