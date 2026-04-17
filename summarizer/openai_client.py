"""OpenAI APIクライアント。"""

from __future__ import annotations

import asyncio
import os

import httpx


async def summarize_with_openai(text: str, max_chars: int = 200) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    prompt = (
        f"以下の記事を日本語で{max_chars}文字以内に要約してください。"
        "初心者にも分かる、短く簡潔な文章にしてください。\n\n"
        f"{text[:6000]}"
    )
    payload = {
        "model": "gpt-4.1-mini",
        "input": prompt,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # 429緩和のため呼び出し前に待機
    await asyncio.sleep(2)

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.openai.com/v1/responses",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()

    content = (data.get("output_text") or "").strip()
    if not content:
        try:
            content = data["output"][0]["content"][0]["text"].strip()
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"OpenAI parse error: {exc}") from exc

    if not content:
        raise RuntimeError("OpenAI returned empty summary")

    return content[:max_chars]
