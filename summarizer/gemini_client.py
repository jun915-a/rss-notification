"""Gemini APIクライアント。"""

from __future__ import annotations

import asyncio
import os
import httpx


async def summarize_with_gemini(text: str, max_chars: int = 200) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "要約して: " + text[:6000]}
                ]
            }
        ]
    }

    headers = {"Content-Type": "application/json"}

    await asyncio.sleep(1.0)

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()

    try:
        content = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )
    except Exception:
        content = ""

    if not content:
        raise RuntimeError(f"Gemini empty response: {data}")

    return content[:max_chars]
