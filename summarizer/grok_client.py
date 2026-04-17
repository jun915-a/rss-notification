"""Grok APIクライアント。"""

from __future__ import annotations

import os
from typing import Optional

import httpx


async def summarize_with_grok(text: str, max_chars: int = 200) -> Optional[str]:
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        return None

    prompt = (
        f"以下の記事を日本語で{max_chars}文字以内に要約してください。"
        "初心者にも分かるように簡潔に書き、必要なら専門用語を短く補足してください。\n\n"
        f"{text}"
    )

    payload = {
        "model": "grok-beta",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post("https://api.x.ai/v1/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            return content[:max_chars]
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] Grok要約失敗: {exc}")
        return None
