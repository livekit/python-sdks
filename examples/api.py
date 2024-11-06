from livekit import api
import asyncio


async def main():
    # will automatically use LIVEKIT_URL, LIVEKIT_API_KEY and LIVEKIT_API_SECRET env vars
    lkapi = api.LiveKitAPI()
    room_info = await lkapi.room.create_room(
        api.CreateRoomRequest(name="my-room"),
    )
    print(room_info)
    room_list = await lkapi.room.list_rooms(api.ListRoomsRequest())
    print(room_list)
    await lkapi.aclose()


if __name__ == "__main__":
    asyncio.run(main())
