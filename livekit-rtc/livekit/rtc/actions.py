from __future__ import annotations

import inspect
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

from .rpc import RpcError

ACTIONS_ATTRIBUTE = "lk.actions"
ACTION_METHOD_PREFIX = "action:"
ACTION_DECLINED_CODE = 1710


@dataclass
class ActionEntry:
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    consent: str = "none"


@dataclass
class ActionContext:
    caller_identity: str


class ActionDeclinedError(Exception):
    def __init__(self, message: str = "action declined") -> None:
        super().__init__(message)


ActionHandler = Callable[[Dict[str, Any], ActionContext], Union[Any, Awaitable[Any]]]


class ActionRegistration:
    def __init__(self, unregister: Callable[[], Awaitable[None]]) -> None:
        self._unregister = unregister

    async def unregister(self) -> None:
        await self._unregister()


def parse_actions(raw: Optional[str]) -> List[ActionEntry]:
    if not raw:
        return []
    try:
        items = json.loads(raw)
    except ValueError:
        return []
    if not isinstance(items, list):
        return []
    return [
        ActionEntry(
            name=item["name"],
            description=item.get("description", ""),
            parameters=item.get("parameters") or {},
            consent=item.get("consent", "none"),
        )
        for item in items
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    ]


def serialize_actions(entries: List[ActionEntry]) -> str:
    return json.dumps([asdict(e) for e in entries])


async def invoke_handler(handler: ActionHandler, payload: str, caller_identity: str) -> str:
    args = json.loads(payload) if payload else {}
    try:
        result = handler(args, ActionContext(caller_identity=caller_identity))
        if inspect.isawaitable(result):
            result = await result
    except ActionDeclinedError as e:
        raise RpcError(ACTION_DECLINED_CODE, str(e)) from e
    return json.dumps(result)
