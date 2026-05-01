from __future__ import annotations

import asyncio
import logging
import os

from dotenv import find_dotenv, load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
    room_io,
)

logger = logging.getLogger("wakeword-agent")


class BasicAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a brief, friendly voice assistant. Answer in one or two "
                "sentences unless the user asks for more detail. When the user says "
                "'bye livekit' or otherwise clearly asks to end the conversation, call "
                "the end_session tool immediately."
            ),
            stt=os.getenv("LIVEKIT_AGENT_STT_MODEL", "deepgram/nova-3"),
            llm=os.getenv("LIVEKIT_AGENT_LLM_MODEL", "openai/gpt-4o-mini"),
            tts=os.getenv("LIVEKIT_AGENT_TTS_MODEL", "cartesia/sonic-2"),
        )

    @function_tool(name="end_session")
    async def end_session(self, ctx: RunContext) -> None:
        """
        End the current voice session when the user says "bye livekit".

        This is the final action for the conversation. Use it only when the user
        clearly says "bye livekit" or otherwise asks to end the session.
        """
        logger.info("ending agent session after user goodbye")
        ctx.session.say("Bye, see you next time.", allow_interruptions=False)
        ctx.session.shutdown()


async def entrypoint(ctx: JobContext) -> None:
    session = AgentSession()
    closed = asyncio.get_running_loop().create_future()
    join_delay = float(os.getenv("LIVEKIT_AGENT_JOIN_DELAY_SECONDS", "2.0"))
    pre_connect_audio_timeout = float(
        os.getenv("LIVEKIT_AGENT_PRECONNECT_AUDIO_TIMEOUT_SECONDS", "10.0")
    )

    @session.on("close")
    def _on_close(_) -> None:
        if not closed.done():
            closed.set_result(None)

    @session.on("user_input_transcribed")
    def _on_user_input_transcribed(ev) -> None:
        logger.info(
            "user transcript%s: %s",
            " final" if ev.is_final else "",
            ev.transcript or "<empty>",
        )

    @session.on("conversation_item_added")
    def _on_conversation_item_added(ev) -> None:
        logger.info("conversation item added: %s", ev.item)

    if join_delay > 0:
        logger.info("delaying agent room join by %.1f seconds", join_delay)
        await asyncio.sleep(join_delay)

    await session.start(
        agent=BasicAssistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                pre_connect_audio=True,
                pre_connect_audio_timeout=pre_connect_audio_timeout,
            ),
        ),
    )
    await closed
    ctx.shutdown("agent session ended")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_dotenv(find_dotenv())

    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name=os.getenv("LIVEKIT_AGENT_NAME", "test-agent"),
        )
    )
