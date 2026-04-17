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
        # xAI側で広く利用されるchat completionsモデル名
        "model": "grok-beta",
        "messages": [
            {"role": "system", "content": "You summarize text briefly."},
            {"role": "user", "content": text[:6000]},
        ],
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # デバッグ用: 送信payloadを明示（機密情報は含めない）
    print(f"[DEBUG] Grok request payload: {payload}")

    async with httpx.AsyncClient(timeout=30) as client:
        await asyncio.sleep(0.7)
        response = await client.post("https://api.x.ai/v1/chat/completions", json=payload, headers=headers)
        if response.status_code >= 400:
            # 400系調査しやすいようレスポンス本文を残す
            raise RuntimeError(f"Grok HTTP {response.status_code}: {response.text}")
        response.raise_for_status()
        data = response.json()

    try:
        content = data["choices"][0]["message"]["content"].strip()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Grok parse error: {exc}") from exc

    if not content:
        raise RuntimeError("Grok returned empty summary")

    return content[:max_chars]
