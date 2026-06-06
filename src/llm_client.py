"""Tiny wrapper around an OpenAI-compatible chat API.

We keep all the LLM "talking" in one small file so the rest of the code never
worries about HTTP details. The same code works with OpenAI, Groq, or any other
provider that speaks the OpenAI chat-completions format -- we just change the
three environment variables.
"""

import os

from openai import OpenAI  # the OpenAI-compatible client library


def _make_client():
    """Build an API client using the env vars. Stop with a clear error if missing."""
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        # SystemExit prints the message and stops the program cleanly.
        raise SystemExit("ERROR: please set the LLM_API_KEY environment variable.")
    # base_url is optional: empty/unset means "use the provider default" (OpenAI).
    base_url = os.environ.get("LLM_BASE_URL") or None
    return OpenAI(api_key=api_key, base_url=base_url)


def ask_llm(prompt, temperature=0.2):
    """Send one prompt to the LLM and return its text answer.

    temperature is kept low (0.2) so the generated tests are more deterministic.
    """
    model = os.environ.get("LLM_MODEL")
    if not model:
        raise SystemExit("ERROR: please set the LLM_MODEL environment variable.")
    client = _make_client()
    # A chat model expects a list of messages; we send a single user message.
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    # The reply text lives at this path in the response object.
    return response.choices[0].message.content
