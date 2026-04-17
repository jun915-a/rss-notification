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
        "model": "grok-beta",
        "messages": [
            {"role": "system", "content": "You summarize text briefly."},
            {"role": "user", "content": text[:6000]},
        ],
        "temperature": 0.2,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    await asyncio.sleep(1.0)

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://api.x.ai/v1/chat/completions",
            json=payload,
            headers=headers,
        )

        if r.status_code >= 400:
            raise RuntimeError(f"Grok error {r.status_code}: {r.text}")

        data = r.json()

    content = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )

    if not content:
        raise RuntimeError("Grok empty response")

    return content[:max_chars]
