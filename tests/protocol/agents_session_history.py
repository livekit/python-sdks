"""Encode a session history the way an installed livekit-agents release uploads it.

livekit-agents 1.7.0 to 1.8.8 fill every field the installed protocol declares on a chat item
from the attribute of the same name, so a new field can break releases already deployed.
Run with one livekit-agents release and the livekit-protocol build under test installed.
"""

from importlib.metadata import version

from livekit.agents import llm

items = [
    llm.ChatMessage(role="user", content=["hi", "there"], extra={"lk.redacted": True}),
    llm.FunctionCall(
        call_id="call_1",
        name="lookup",
        arguments="{}",
        extra={
            "google": {"thought_signature": "c2ln"},
            "__livekit_agents_tool_non_blocking": True,
        },
    ),
    llm.FunctionCallOutput(call_id="call_1", name="lookup", output="ok", is_error=False),
]
llm.ChatContext(items).to_proto().SerializeToString()
print(
    f"livekit-agents {version('livekit-agents')} with livekit-protocol {version('livekit-protocol')}: ok"
)
