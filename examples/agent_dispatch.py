import asyncio
from livekit import api

room_name = "my-room"
agent_name = "test-agent"

"""
This example demonstrates how to have an agent join a room 
without using the automatic dispatch. In order to use this 
feature, you must have an agent running with `agent_name` set 
when defining your WorkerOptions. A dispatch requests the 
agent to enter a specific room with optional metadata.
"""


async def create_explicit_dispatch():
    lkapi = api.LiveKitAPI()

    dispatch = await lkapi.agent_dispatch.create_dispatch(
        api.CreateAgentDispatchRequest(
            agent_name=agent_name, room=room_name, metadata="my_metadata"
        )
    )
    print("created dispatch", dispatch)

    dispatches = await lkapi.agent_dispatch.list_dispatch(room_name=room_name)
    print(f"there are {len(dispatches)} dispatches in {room_name}")
    await lkapi.aclose()


"""
When agent name is set, the agent will no longer be automatically dispatched
to new rooms. If you want that agent to be dispatched to a new room as soon as
the participant connects, you can set the RoomConfiguration with the agent
definition in the access token.
"""


async def create_token_with_agent_dispatch() -> str:
    token = (
        api.AccessToken()
        .with_identity("my_participant")
        .with_grants(api.VideoGrants(room_join=True, room=room_name))
        .with_room_config(
            api.RoomConfiguration(
                agents=[api.RoomAgentDispatch(agent_name="test-agent", metadata="my_metadata")],
            ),
        )
        .to_jwt()
    )
    return token


async def main():
    token = await create_token_with_agent_dispatch()
    print("created participant token", token)
    print("creating explicit dispatch")
    await create_explicit_dispatch()


asyncio.run(main())
