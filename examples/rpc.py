from livekit import rtc, api
import os
import json
import asyncio
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local", override=False)
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET or not LIVEKIT_URL:
    raise ValueError(
        "Missing required environment variables. Please check your .env.local file."
    )


async def main():
    room_name = f"rpc-test-{os.urandom(4).hex()}"

    print(f"Connecting participants to room: {room_name}")

    callers_room, greeters_room, math_genius_room = await asyncio.gather(
        connect_participant("caller", room_name),
        connect_participant("greeter", room_name),
        connect_participant("math-genius", room_name),
    )

    # Register all methods for the receiving participant
    await register_receiver_methods(greeters_room, math_genius_room)

    try:
        print("\n\nRunning greeting example...")
        await asyncio.gather(perform_greeting(callers_room))
    except Exception as error:
        print("Error:", error)

    try:
        print("\n\nRunning error handling example...")
        await perform_divide(callers_room)
    except Exception as error:
        print("Error:", error)

    try:
        print("\n\nRunning math example...")
        await perform_square_root(callers_room)
        await asyncio.sleep(2)
        await perform_quantum_hypergeometric_series(callers_room)
    except Exception as error:
        print("Error:", error)

    print("\n\nParticipants done, disconnecting...")
    await callers_room.disconnect()
    await greeters_room.disconnect()
    await math_genius_room.disconnect()

    print("Participants disconnected. Example completed.")


async def register_receiver_methods(
    greeters_room: rtc.Room, math_genius_room: rtc.Room
):
    async def arrival_method(
        request_id: str,
        caller: rtc.RemoteParticipant,
        payload: str,
        response_timeout_ms: int,
    ):
        print(f'[Greeter] Oh {caller.identity} arrived and said "{payload}"')
        await asyncio.sleep(2)
        return "Welcome and have a wonderful day!"

    async def square_root_method(
        request_id: str,
        caller: rtc.RemoteParticipant,
        payload: str,
        response_timeout_ms: int,
    ):
        json_data = json.loads(payload)
        number = json_data["number"]
        print(
            f"[Math Genius] I guess {caller.identity} wants the square root of {number}. I've only got {response_timeout_ms / 1000} seconds to respond but I think I can pull it off."
        )

        print("[Math Genius] *doing math*…")
        await asyncio.sleep(2)

        result = number**0.5
        print(f"[Math Genius] Aha! It's {result}")
        return json.dumps({"result": result})

    async def divide_method(
        request_id: str,
        caller: rtc.RemoteParticipant,
        payload: str,
        response_timeout_ms: int,
    ):
        json_data = json.loads(payload)
        dividend = json_data["dividend"]
        divisor = json_data["divisor"]
        print(f"[Math Genius] {caller.identity} wants to divide {dividend} by {divisor}.")
        
        result = dividend / divisor
        return json.dumps({"result": result})

    await greeters_room.local_participant.register_rpc_method("arrival", arrival_method)
    await math_genius_room.local_participant.register_rpc_method(
        "square-root", square_root_method
    )
    await math_genius_room.local_participant.register_rpc_method(
        "divide", divide_method
    )


async def perform_greeting(room: rtc.Room):
    print("[Caller] Letting the greeter know that I've arrived")
    try:
        response = await room.local_participant.perform_rpc(
            "greeter", "arrival", "Hello"
        )
        print(f'[Caller] That\'s nice, the greeter said: "{response}"')
    except Exception as error:
        print(f"[Caller] RPC call failed: {error}")
        raise


async def perform_square_root(room: rtc.Room):
    print("[Caller] What's the square root of 16?")
    try:
        response = await room.local_participant.perform_rpc(
            "math-genius", "square-root", json.dumps({"number": 16})
        )
        parsed_response = json.loads(response)
        print(f"[Caller] Nice, the answer was {parsed_response['result']}")
    except Exception as error:
        print(f"[Caller] RPC call failed: {error}")
        raise


async def perform_quantum_hypergeometric_series(room: rtc.Room):
    print("[Caller] What's the quantum hypergeometric series of 42?")
    try:
        response = await room.local_participant.perform_rpc(
            "math-genius", "quantum-hypergeometric-series", json.dumps({"number": 42})
        )
        parsed_response = json.loads(response)
        print(f"[Caller] genius says {parsed_response['result']}!")
    except rtc.RpcError as error:
        if error.code == rtc.RpcError.ErrorCode.UNSUPPORTED_METHOD:
            print("[Caller] Aww looks like the genius doesn't know that one.")
            return
        print("[Caller] Unexpected error:", error)
        raise
    except Exception as error:
        print("[Caller] Unexpected error:", error)
        raise


async def perform_divide(room: rtc.Room):
    print("[Caller] Let's divide 10 by 0.")
    try:
        response = await room.local_participant.perform_rpc(
            "math-genius", "divide", json.dumps({"dividend": 10, "divisor": 0})
        )
        parsed_response = json.loads(response)
        print(f"[Caller] The result is {parsed_response['result']}")
    except rtc.RpcError as error:
        if error.code == rtc.RpcError.ErrorCode.APPLICATION_ERROR:
            print("[Caller] Aww something went wrong with that one, lets try something else.")
        else:
            print(f"[Caller] RPC call failed with unexpected RpcError: {error}")
    except Exception as error:
        print(f"[Caller] RPC call failed with unexpected error: {error}")


def create_token(identity: str, room_name: str):
    token = (
        api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(identity)
        .with_grants(
            api.VideoGrants(
                room=room_name,
                room_join=True,
                can_publish=True,
                can_subscribe=True,
            )
        )
    )
    return token.to_jwt()


async def connect_participant(identity: str, room_name: str) -> rtc.Room:
    room = rtc.Room()
    token = create_token(identity, room_name)

    def on_disconnected(reason: str):
        print(f"[{identity}] Disconnected from room: {reason}")

    room.on("disconnected", on_disconnected)

    await room.connect(LIVEKIT_URL, token)

    async def wait_for_participants():
        if room.remote_participants:
            return
        participant_connected = asyncio.Event()

        def _on_participant_connected(participant: rtc.RemoteParticipant):
            room.off("participant_connected", _on_participant_connected)
            participant_connected.set()

        room.on("participant_connected", _on_participant_connected)
        await participant_connected.wait()

    try:
        await asyncio.wait_for(wait_for_participants(), timeout=5.0)
    except asyncio.TimeoutError:
        raise TimeoutError("Timed out waiting for participants")

    return room


if __name__ == "__main__":
    asyncio.run(main())
