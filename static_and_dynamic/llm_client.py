# llm_client.py
"""
LLM API client. Reads API key from environment variable, never hardcode keys in source.
"""
import os
from openai import OpenAI  # DeepSeek dùng OpenAI-compatible API

_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError(
                "DEEPSEEK_API_KEY not set. Set it via environment variable, "
                "e.g. `set DEEPSEEK_API_KEY=your_key_here` (Windows) "
                "or `export DEEPSEEK_API_KEY=your_key_here` (Linux/Mac)."
            )
        _client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    return _client


def call_llm(prompt: str, model: str = "deepseek-chat", temperature: float = 0) -> str:
    """Calls the DeepSeek API and returns the raw text response."""
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content