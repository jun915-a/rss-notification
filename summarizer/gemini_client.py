"""Gemini APIクライアント。"""

from __future__ import annotations

import asyncio
import os

import httpx


async def summarize_with_gemini(text: str, max_chars: int = 200) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "要約して: " + text[:6000]},
                ]
            }
        ]
    }

    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}

    async with httpx.AsyncClient(timeout=30) as client:
        await asyncio.sleep(0.7)
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    try:
        content = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Gemini parse error: {exc}") from exc

    if not content:
        raise RuntimeError("Gemini returned empty summary")

    return content[:max_chars]
