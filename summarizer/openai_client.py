"""OpenAI APIクライアント。"""

from __future__ import annotations

import asyncio
import os
import httpx


async def summarize_with_openai(text: str, max_chars: int = 200) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    prompt = f"次を{max_chars}文字以内で要約:\n\n{text[:6000]}"

    payload = {
        "model": "gpt-4.1-mini",
        "input": prompt,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    await asyncio.sleep(2.0)

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://api.openai.com/v1/responses",
            json=payload,
            headers=headers,
        )

        if r.status_code == 429:
            raise RuntimeError("OpenAI rate limit (429)")

        r.raise_for_status()
        data = r.json()

    content = data.get("output_text", "").strip()
    if not content:
        raise RuntimeError("OpenAI empty response")

    return content[:max_chars]
