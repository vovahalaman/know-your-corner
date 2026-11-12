"""AI access: the only module that imports the Gemini SDK."""

from google import genai

from know_your_corner import config, prompts

client = genai.Client(api_key=config.GOOGLE_API_KEY)


def reply(messages: list[dict[str, str]]) -> str:
    """Send the conversation to Gemini and return the answer text."""
    # build Gemini history from session state
    gemini_history = [
        genai.types.Content(
            role=m["role"] if m["role"] == "user" else "model",
            parts=[genai.types.Part(text=m["content"])],
        )
        for m in messages
    ]
    response = client.models.generate_content(
        model=config.MODEL,
        contents=gemini_history,
        config=genai.types.GenerateContentConfig(
            system_instruction=prompts.SYSTEM_INSTRUCTION,
        ),
    )
    return response.text
