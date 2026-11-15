"""AI access: the only module that imports the Gemini SDK."""

from dataclasses import dataclass
from functools import cache
from typing import Any

from google import genai

from know_your_corner import config


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ModelReply:
    interaction_id: str
    status: str
    text: str
    calls: list[ToolCall]


@cache
def _client() -> genai.Client:
    if not config.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is not set. Copy .env.example to .env and add your key.")
    return genai.Client(api_key=config.GOOGLE_API_KEY)


def send(
    input: str | list[dict[str, Any]],
    system_instruction: str,
    tools: list[dict[str, Any]],
    previous_interaction_id: str | None,
) -> ModelReply:
    interaction = _client().interactions.create(
        model=config.MODEL,
        input=input,
        system_instruction=system_instruction,
        tools=tools,
        previous_interaction_id=previous_interaction_id,
    )
    calls = [
        ToolCall(id=s.id, name=s.name, arguments=s.arguments or {})
        for s in interaction.steps or []
        if s.type == "function_call"
    ]
    return ModelReply(
        interaction_id=interaction.id,
        status=interaction.status,
        text=interaction.output_text or "",
        calls=calls,
    )
