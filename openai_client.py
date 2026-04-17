"""OpenAI Responses API client."""

from __future__ import annotations

import os

import httpx


async def summarize_with_openai(text: str, max_chars: int) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    prompt = (
        f"以下を日本語で{max_chars}文字以内に要約してください。"
        "初心者にも分かる簡潔な説明にしてください。\n\n"
        f"{text[:6000]}"
    )

    payload = {
        "model": "gpt-4.1-mini",
        "input": prompt,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post("https://api.openai.com/v1/responses", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    output_text = (data.get("output_text") or "").strip()
    if not output_text:
        # output_textが空の場合のフォールバック抽出
        try:
            output_items = data.get("output", [])
            output_text = output_items[0]["content"][0]["text"].strip()
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"OpenAI response parse error: {exc}") from exc

    if not output_text:
        raise RuntimeError("OpenAI returned empty summary")

    return output_text[:max_chars]
