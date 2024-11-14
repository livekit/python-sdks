import aiohttp
from typing import Optional
from livekit.protocol.agent_dispatch import (
    CreateAgentDispatchRequest,
    AgentDispatch,
    DeleteAgentDispatchRequest,
    ListAgentDispatchRequest,
    ListAgentDispatchResponse,
)
from ._service import Service
from .access_token import VideoGrants

SVC = "AgentDispatchService"
"""@private"""


class AgentDispatchService(Service):
    """Manage agent dispatches. Service APIs require roomAdmin permissions.

    Recommended way to use this service is via `livekit.api.LiveKitAPI`:

    ```python
    from livekit import api
    lkapi = api.LiveKitAPI()
    agent_dispatch = lkapi.agent_dispatch
    ```
    """

    def __init__(
        self, session: aiohttp.ClientSession, url: str, api_key: str, api_secret: str
    ):
        super().__init__(session, url, api_key, api_secret)

    async def create_dispatch(self, req: CreateAgentDispatchRequest) -> AgentDispatch:
        """Create an explicit dispatch for an agent to join a room.

        To use explicit dispatch, your agent must be registered with an `agentName`.

        Args:
            req (CreateAgentDispatchRequest): Request containing dispatch creation parameters

        Returns:
            AgentDispatch: The created agent dispatch object
        """
        return await self._client.request(
            SVC,
            "CreateDispatch",
            req,
            self._auth_header(VideoGrants(room_admin=True, room=req.room)),
            AgentDispatch,
        )

    async def delete_dispatch(self, dispatch_id: str, room_name: str) -> AgentDispatch:
        """Delete an explicit dispatch for an agent in a room.

        Args:
            dispatch_id (str): ID of the dispatch to delete
            room_name (str): Name of the room containing the dispatch

        Returns:
            AgentDispatch: The deleted agent dispatch object
        """
        return await self._client.request(
            SVC,
            "DeleteDispatch",
            DeleteAgentDispatchRequest(
                dispatch_id=dispatch_id,
                room=room_name,
            ),
            self._auth_header(VideoGrants(room_admin=True, room=room_name)),
            AgentDispatch,
        )

    async def list_dispatch(self, room_name: str) -> list[AgentDispatch]:
        """List all agent dispatches in a room.

        Args:
            room_name (str): Name of the room to list dispatches from

        Returns:
            list[AgentDispatch]: List of agent dispatch objects in the room
        """
        res = await self._client.request(
            SVC,
            "ListDispatch",
            ListAgentDispatchRequest(room=room_name),
            self._auth_header(VideoGrants(room_admin=True, room=room_name)),
            ListAgentDispatchResponse,
        )
        return list(res.agent_dispatches)

    async def get_dispatch(
        self, dispatch_id: str, room_name: str
    ) -> Optional[AgentDispatch]:
        """Get an Agent dispatch by ID

        Args:
            dispatch_id (str): ID of the dispatch to retrieve
            room_name (str): Name of the room containing the dispatch

        Returns:
            Optional[AgentDispatch]: The requested agent dispatch object if found, None otherwise
        """
        res = await self._client.request(
            SVC,
            "ListDispatch",
            ListAgentDispatchRequest(dispatch_id=dispatch_id, room=room_name),
            self._auth_header(VideoGrants(room_admin=True, room=room_name)),
            ListAgentDispatchResponse,
        )
        if len(res.agent_dispatches) > 0:
            return res.agent_dispatches[0]
        return None
