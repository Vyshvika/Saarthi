"""
Thin wrapper around the underlying language-model provider.

Kept in its own module, behind a generic interface, so the rest of the app
never talks to a specific vendor SDK directly - only to `generate_reply`
and `stream_reply`. This also means swapping providers later only touches
this one file. Currently backed by Groq's free-tier API (OpenAI-compatible).
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

_API_KEY = os.getenv("AI_API_KEY")
_MODEL = os.getenv("AI_MODEL", "llama-3.3-70b-versatile")

_client = Groq(api_key=_API_KEY)


def _build_messages(system_prompt: str, conversation: list[dict]) -> list[dict]:
    return [{"role": "system", "content": system_prompt}] + conversation


def stream_reply(system_prompt: str, conversation: list[dict]):
    """
    conversation: list of {"role": "user"|"assistant", "content": str}
    Yields text chunks as they arrive.
    """
    stream = _client.chat.completions.create(
        model=_MODEL,
        max_tokens=1500,
        messages=_build_messages(system_prompt, conversation),
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def generate_reply(system_prompt: str, conversation: list[dict]) -> str:
    response = _client.chat.completions.create(
        model=_MODEL,
        max_tokens=1500,
        messages=_build_messages(system_prompt, conversation),
    )
    return response.choices[0].message.content