"""AI access: the only module that imports the Gemini SDK."""

from dataclasses import dataclass
from functools import cache

from google import genai

from know_your_corner import config


@dataclass(frozen=True)
class ModelReply:
    interaction_id: str
    status: str
    text: str


@cache
def _client() -> genai.Client:
    if not config.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is not set. Copy .env.example to .env and add your key.")
    return genai.Client(api_key=config.GOOGLE_API_KEY)


def send(message: str, system_instruction: str, previous_interaction_id: str | None) -> ModelReply:
    interaction = _client().interactions.create(
        model=config.MODEL,
        input=message,
        system_instruction=system_instruction,
        previous_interaction_id=previous_interaction_id,
    )
    return ModelReply(
        interaction_id=interaction.id,
        status=interaction.status,
        text=interaction.output_text or "",
    )