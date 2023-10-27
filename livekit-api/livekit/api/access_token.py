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
import datetime

import jwt

DEFAULT_TTL = datetime.timedelta(hours=6)


@dataclasses.dataclass
class VideoGrants:
    # actions on rooms
    room_create: bool = False
    room_list: bool = False
    room_record: bool = False

    # actions on a particular room
    room_admin: bool = False
    room_join: bool = False
    room: str = ""

    # permissions within a room
    can_publish: bool = True
    can_subscribe: bool = True
    can_publish_data: bool = True

    # TrackSource types that a participant may publish.
    # When set, it supercedes CanPublish. Only sources explicitly set here can be
    # published
    can_publish_sources: list[str] = dataclasses.field(default_factory=list)

    # by default, a participant is not allowed to update its own metadata
    can_update_own_metadata: bool = False

    # actions on ingresses
    ingress_admin: bool = False  # applies to all ingress

    # participant is not visible to other participants (useful when making bots)
    hidden: bool = False

    # indicates to the room that current participant is a recorder
    recorder: bool = False


@dataclasses.dataclass
class Claims:
    name: str = ""
    video: VideoGrants = dataclasses.field(default_factory=VideoGrants)
    metadata: str = ""
    sha256: str = ""


class AccessToken:
    def __init__(self, api_key: str, api_secret: str) -> None:
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

    def with_identity(self, identity: str) -> "AccessToken":
        self.identity = identity
        return self

    def with_name(self, name: str) -> "AccessToken":
        self.claims.name = name
        return self

    def with_metadata(self, metadata: str) -> "AccessToken":
        self.claims.metadata = metadata
        return self

    def with_sha256(self, sha256: str) -> "AccessToken":
        self.claims.sha256 = sha256
        return self

    def to_jwt(self) -> str:
        def camel_case_dict(data) -> dict:
            return {
                "".join(
                    word if i == 0 else word.title()
                    for i, word in enumerate(key.split("_"))
                ): value
                for key, value in data
                if value is not None
            }

        claims = dataclasses.asdict(self.claims)
        claims.update(
            {
                "sub": self.identity,
                "iss": self.api_key,
                "nbf": calendar.timegm(datetime.datetime.utcnow().utctimetuple()),
                "exp": calendar.timegm(
                    (datetime.datetime.utcnow() + self.ttl).utctimetuple()
                ),
                "video": dataclasses.asdict(
                    self.claims.video, dict_factory=camel_case_dict
                ),
            }
        )

        return jwt.encode(claims, self.api_secret, algorithm="HS256")
