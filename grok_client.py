"""Grok API client."""

from __future__ import annotations

import os

import httpx


async def summarize_with_grok(text: str, max_chars: int) -> str:
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        raise RuntimeError("GROK_API_KEY is not set")

    prompt = (
        f"以下を日本語で{max_chars}文字以内に要約してください。"
        "初心者にも分かるように簡潔に説明してください。\n\n"
        f"{text[:6000]}"
    )
    payload = {
        "model": "grok-1",
        "messages": [
            {"role": "system", "content": "あなたは簡潔な日本語要約アシスタントです。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post("https://api.x.ai/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    try:
        summary = data["choices"][0]["message"]["content"].strip()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Grok response parse error: {exc}") from exc

    if not summary:
        raise RuntimeError("Grok returned empty summary")

    return summary[:max_chars]
