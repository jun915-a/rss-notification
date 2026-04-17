"""要約フォールバック実装。"""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable

from summarizer.openai_client import summarize_with_openai
from summarizer.gemini_client import summarize_with_gemini
from summarizer.grok_client import summarize_with_grok


async def summarize_text(text: str, max_chars: int = 200) -> str:
    fallback = (text or "要約対象なし").strip()[:max_chars]

    providers = [
        ("OpenAI", summarize_with_openai),
        ("Gemini", summarize_with_gemini),
        ("Grok", summarize_with_grok),
    ]

    for name, fn in providers:
        try:
            await asyncio.sleep(1.0)  # レート制御
            return await fn(text, max_chars)
        except Exception as e:
            print(f"[WARN] {name}失敗: {e}")

    print("[WARN] 全要約API失敗: フォールバック返却")
    return fallback
