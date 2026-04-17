"""要約フォールバック実装。"""

from __future__ import annotations

from summarizer.gemini_client import summarize_with_gemini
from summarizer.grok_client import summarize_with_grok
from summarizer.openai_client import summarize_with_openai


async def summarize_text(text: str, max_chars: int = 200) -> str:
    try:
        return await summarize_with_openai(text, max_chars=max_chars)
    except Exception as openai_error:  # noqa: BLE001
        print(f"[WARN] OpenAI要約失敗: {openai_error}")

    try:
        return await summarize_with_gemini(text, max_chars=max_chars)
    except Exception as gemini_error:  # noqa: BLE001
        print(f"[WARN] Gemini要約失敗: {gemini_error}")

    try:
        return await summarize_with_grok(text, max_chars=max_chars)
    except Exception as grok_error:  # noqa: BLE001
        print(f"[WARN] Grok要約失敗: {grok_error}")

    print("[WARN] 全要約API失敗: 生テキストを返却")
    return text[:max_chars]
