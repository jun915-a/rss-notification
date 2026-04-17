"""要約簡略実装。"""

from __future__ import annotations

async def summarize_text(text: str, max_chars: int = 200) -> str:
    return text[:max_chars]
