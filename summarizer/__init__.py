"""要約フォールバック実装。"""

from __future__ import annotations

import asyncio

from summarizer.gemini_client import summarize_with_gemini
from summarizer.grok_client import summarize_with_grok
from summarizer.openai_client import summarize_with_openai


async def summarize_text(text: str, max_chars: int = 200) -> str:
    preview = text[:3500]

    for name, func in [
        ("OpenAI", summarize_with_openai),
        ("Gemini", summarize_with_gemini),
        ("Grok", summarize_with_grok),
    ]:
        for attempt in range(2):
            try:
                summary = await func(preview, max_chars=max_chars)
                if summary:
                    print(f"[INFO] 要約成功: {name}")
                    return summary
            except Exception as exc:  # noqa: BLE001
                print(f"[WARN] {name}要約失敗 (attempt {attempt + 1}/2): {exc}")
                await asyncio.sleep(2)

    print("[ERROR] 全要約API失敗")
    return ""
