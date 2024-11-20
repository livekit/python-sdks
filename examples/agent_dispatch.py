import asyncio
import os
import aiohttp
from livekit.protocol.room import RoomConfiguration
from livekit.protocol.agent_dispatch import (
    RoomAgentDispatch,
    CreateAgentDispatchRequest,
)
from livekit.api import AccessToken, VideoGrants
from livekit.api.agent_dispatch_service import AgentDispatchService


room_name = "my-room"
agent_name = "test-agent"

"""
This example demonstrates how to have an agent join a room 
without using the automatic dispatch. In order to use this 
feature, you must have an agent running with `agentName` set 
when defining your WorkerOptions. A dispatch requests the 
agent to enter a specific room with optional metadata.
"""


async def create_explicit_disptach(http_session: aiohttp.ClientSession):
    agent_disptach_service = AgentDispatchService(
        session=http_session,
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
    )
    dispatch_request = CreateAgentDispatchRequest(
        agent_name=agent_name, room=room_name, metadata="my_metadata"
    )
    dispatch = await agent_disptach_service.create_dispatch(dispatch_request)
    print("created dispatch", dispatch)
    dispatches = await agent_disptach_service.list_dispatch(room_name=room_name)
    print(f"there are {len(dispatches)} dispatches in {room_name}")


"""
When agent name is set, the agent will no longer be automatically dispatched
to new rooms. If you want that agent to be dispatched to a new room as soon as
the participant connects, you can set the roomConfig with the agent
definition in the access token.
"""


async def create_token_with_agent_dispatch() -> str:
    token = (
        AccessToken()
        .with_identity("my_participant")
        .with_grants(VideoGrants(room_join=True, room=room_name))
        .with_room_config(
            RoomConfiguration(
                agents=[
                    RoomAgentDispatch(agent_name="test-agent", metadata="my_metadata")
                ],
            ),
        )
        .to_jwt()
    )
    return token


async def main():
    async with aiohttp.ClientSession() as http_session:
        token = await create_token_with_agent_dispatch()
        print("created participant token", token)
        print("creating explicit dispatch")
        await create_explicit_disptach(http_session)


asyncio.run(main())
