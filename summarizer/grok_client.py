"""Grok APIクライアント。"""

from __future__ import annotations

import asyncio
import os

import httpx


async def summarize_with_grok(text: str, max_chars: int = 200) -> str:
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        raise RuntimeError("GROK_API_KEY is not set")

    payload = {
        "model": "grok-1",
        "messages": [
            {"role": "system", "content": "You summarize text briefly."},
            {"role": "user", "content": text[:6000]},
        ],
        "temperature": 0.2,
        "max_tokens": 300,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=30) as client:
        await asyncio.sleep(0.7)
        response = await client.post("https://api.x.ai/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    try:
        content = data["choices"][0]["message"]["content"].strip()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Grok parse error: {exc}") from exc

    if not content:
        raise RuntimeError("Grok returned empty summary")

    return content[:max_chars]
