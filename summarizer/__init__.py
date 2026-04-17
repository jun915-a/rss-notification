"""OpenAI専用の要約実装。"""

from __future__ import annotations

from summarizer.openai_client import summarize_with_openai


async def summarize_text(text: str, max_chars: int = 200) -> str:
    try:
        return await summarize_with_openai(text, max_chars=max_chars)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] OpenAI要約失敗: {exc}")
        return text[:max_chars]
