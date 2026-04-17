"""Gemini API client."""

from __future__ import annotations

import os

import httpx


async def summarize_with_gemini(text: str, max_chars: int) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    prompt = (
        f"以下を日本語で{max_chars}文字以内に要約してください。"
        "初心者にも分かるように簡潔に説明してください。\n\n"
        f"{text[:6000]}"
    )

    url = (
        "https://generativelanguage.googleapis.com/v1/models/"
        f"gemini-1.5-flash:generateContent?key={api_key}"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    try:
        summary = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Gemini response parse error: {exc}") from exc

    if not summary:
        raise RuntimeError("Gemini returned empty summary")

    return summary[:max_chars]
