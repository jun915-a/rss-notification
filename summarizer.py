"""Summary fallback orchestrator."""

from __future__ import annotations

import asyncio

from gemini_client import summarize_with_gemini
from grok_client import summarize_with_grok
from openai_client import summarize_with_openai


async def summarize_text(text: str, max_chars: int = 200) -> str:
    # OpenAI
    for _ in range(2):
        try:
            return await summarize_with_openai(text, max_chars)
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] OpenAI要約失敗: {exc}")
            await asyncio.sleep(2)

    # Gemini
    for _ in range(2):
        try:
            return await summarize_with_gemini(text, max_chars)
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] Gemini要約失敗: {exc}")
            await asyncio.sleep(2)

    # Grok
    for _ in range(2):
        try:
            return await summarize_with_grok(text, max_chars)
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] Grok要約失敗: {exc}")
            await asyncio.sleep(2)

    print("[ERROR] 全要約API失敗")
    return ""
