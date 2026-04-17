"""Gemini APIクライアント。"""

from __future__ import annotations

import os
from typing import Optional

import httpx


async def summarize_with_gemini(text: str, max_chars: int = 200) -> Optional[str]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    prompt = (
        f"以下の記事を日本語で{max_chars}文字以内に要約してください。"
        "初心者向けに簡潔にし、必要なら専門用語を補足してください。\n\n"
        f"{text}"
    )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={api_key}"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return content[:max_chars]
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] Gemini要約失敗: {exc}")
        return None
