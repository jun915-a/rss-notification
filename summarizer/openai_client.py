"""OpenAI APIクライアント。"""

from __future__ import annotations

import os
from typing import Optional

import httpx


async def summarize_with_openai(text: str, max_chars: int = 200) -> Optional[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "あなたは要約アシスタントです。"
                    "日本語で簡潔に、初心者にも分かる要約を返してください。"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"次の記事を日本語で{max_chars}文字以内に要約してください。"
                    "必要なら専門用語を短く補足してください。\n\n"
                    f"{text}"
                ),
            },
        ],
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            return content[:max_chars]
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] OpenAI要約失敗: {exc}")
        return None
