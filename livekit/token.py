import calendar
import dataclasses
import datetime
import typing as t

import jwt


DEFAULT_TOKEN_TTL = datetime.timedelta(hours=6)

def camel_case_dict(data) -> dict:
    """
    Return dictionary with keys converted from snake_case to camelCase

    Example:
        dataclasses.asdict(my_data, dict_factory=camel_case_dict)
    """
    return {
        "".join(
            word if i == 0 else word.title() for i, word in enumerate(key.split("_"))
        ): value
        for key, value in data
        if value is not None
    }

@dataclasses.dataclass
class VideoGrant:
    room_create: t.Optional[bool] = None
    room_join: t.Optional[bool] = None
    room_list: t.Optional[bool] = None
    room_record: t.Optional[bool] = None
    room_admin: t.Optional[bool] = None
    room: t.Optional[str] = None
    can_publish: t.Optional[bool] = None
    can_subscribe: t.Optional[bool] = None
    can_publish_data: t.Optional[bool] = None
    hidden: t.Optional[bool] = None


@dataclasses.dataclass
class AccessToken:
    api_key: str
    api_secret: str
    grant: VideoGrant = dataclasses.field(default_factory=VideoGrant)
    identity: t.Optional[str] = None
    name: t.Optional[str] = None
    ttl: datetime.timedelta = DEFAULT_TOKEN_TTL
    metadata: t.Optional[str] = None

    def __post_init__(self):
        if self.grant.room_join and self.identity is None:
            raise ValueError("identity is required for room_join grant")
        if self.ttl.total_seconds() <= 0:
            raise ValueError("AccessToken must expire in the future.")

    def to_jwt(self) -> str:
        payload = {
            "video": dataclasses.asdict(
                self.grant, dict_factory=camel_case_dict
            ),
            "iss": self.api_key,
            "nbf": calendar.timegm(datetime.datetime.utcnow().utctimetuple()),
            "exp": calendar.timegm(
                (datetime.datetime.utcnow() + self.ttl).utctimetuple()
            ),
        }
        if self.metadata is not None:
            payload["metadata"] = self.metadata
        if self.identity is not None:
            payload["sub"] = self.identity
        if self.name:
            payload["name"] = self.name
        return jwt.encode(payload, self.api_secret)


def create_access_token(
        api_key: str, api_secret: str, room_name: str, identity: str
) -> str:
    grant = VideoGrant(room_join=True, room=room_name)
    token = AccessToken(api_key, api_secret, identity=identity, grant=grant)
    r: str = token.to_jwt()
    return r

