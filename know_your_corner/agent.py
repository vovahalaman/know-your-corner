"""The agent: one user message in, one answer out (issue #9).

The interface calls only handle(); it never talks to the model directly.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any

from know_your_corner import llm, prompts, tools

log = logging.getLogger(__name__)

MAX_ROUNDS = 8

FALLBACK = "Sorry, I couldn't answer that just now. Please try again in a moment."
TOO_MANY_ROUNDS = "I couldn't finish that one. Could you ask a narrower question, for example about one neighborhood?"


@dataclass(frozen=True)
class Turn:
    text: str
    interaction_id: str | None
    ok: bool


def _run_calls(calls: list[llm.ToolCall]) -> list[dict[str, Any]]:
    results = []
    for call in calls:
        result = tools.run_tool(call.name, call.arguments)
        is_error = "error" in result
        log.info("tool %s(%s) -> %s", call.name, call.arguments, "error" if is_error else "ok")
        results.append(
            {
                "type": "function_result",
                "call_id": call.id,
                "name": call.name,
                "result": json.dumps(result, ensure_ascii=False),
                "is_error": is_error,
            }
        )
    return results


def handle(user_text: str, previous_interaction_id: str | None) -> Turn:
    input: str | list[dict[str, Any]] = prompts.wrap_message(user_text)
    interaction_id = previous_interaction_id

    for _ in range(MAX_ROUNDS):
        try:
            reply = llm.send(
                input=input,
                system_instruction=prompts.system_instruction(),
                tools=tools.DECLARATIONS,
                previous_interaction_id=interaction_id,
            )
        except Exception:
            log.exception("model request failed")
            return Turn(FALLBACK, previous_interaction_id, ok=False)

        if reply.calls:
            input = _run_calls(reply.calls)
            interaction_id = reply.interaction_id
            continue

        if reply.status != "completed" or not reply.text.strip():
            log.warning("unusable reply: status=%s, text length=%d", reply.status, len(reply.text))
            return Turn(FALLBACK, previous_interaction_id, ok=False)

        return Turn(reply.text, reply.interaction_id, ok=True)

    log.warning("stopped after %d rounds", MAX_ROUNDS)
    return Turn(TOO_MANY_ROUNDS, previous_interaction_id, ok=False)
