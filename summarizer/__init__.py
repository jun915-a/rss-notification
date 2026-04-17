"""要約フォールバック実装。"""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable

from summarizer.gemini_client import summarize_with_gemini
from summarizer.grok_client import summarize_with_grok
from summarizer.openai_client import summarize_with_openai


async def _run_with_single_retry(
    provider_name: str,
    provider_func: Callable[[str, int], Awaitable[str]],
    text: str,
    max_chars: int,
) -> str:
    # 最大1回リトライ（合計2回試行）
    for attempt in range(2):
        try:
            return await provider_func(text, max_chars)
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] {provider_name}要約失敗 (attempt {attempt + 1}/2): {exc}")
            if attempt == 0:
                await asyncio.sleep(0.7)
    raise RuntimeError(f"{provider_name} failed after retry")


async def summarize_text(text: str, max_chars: int = 200) -> str:
    fallback = (text or "")[:max_chars]

    providers = [
        ("OpenAI", summarize_with_openai, 5),
        ("Gemini", summarize_with_gemini, 2),
        ("Grok", summarize_with_grok, 1),
    ]

    for name, fn, wait in providers:
        try:
            await asyncio.sleep(wait)
            return await fn(text, max_chars)
        except Exception as e:
            print(f"[WARN] {name}失敗: {e}")

    return fallback
