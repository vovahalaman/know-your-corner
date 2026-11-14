"""The agent: one user message in, one answer out (issue #9).

The interface calls only handle(); it never talks to the model directly.
The tool loop (MAX_ROUNDS, run_tool) will live here.
"""

import logging
from dataclasses import dataclass

from know_your_corner import llm, prompts

log = logging.getLogger(__name__)

FALLBACK = "Sorry, I couldn't answer that just now. Please try again in a moment."


@dataclass(frozen=True)
class Turn:
    text: str
    interaction_id: str | None
    ok: bool


def handle(user_text: str, previous_interaction_id: str | None) -> Turn:
    try:
        reply = llm.send(
            message=prompts.wrap_message(user_text),
            system_instruction=prompts.system_instruction(),
            previous_interaction_id=previous_interaction_id,
        )
    except Exception:
        log.exception("model request failed")
        return Turn(FALLBACK, previous_interaction_id, ok=False)

    if reply.status != "completed" or not reply.text.strip():
        log.warning("unusable reply: status=%s, text length=%d", reply.status, len(reply.text))
        return Turn(FALLBACK, previous_interaction_id, ok=False)

    return Turn(reply.text, reply.interaction_id, ok=True)