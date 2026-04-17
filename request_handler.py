"""ユーザー検索リクエスト処理。"""

from __future__ import annotations

from typing import Dict, List, Set

from filter import filter_articles_by_query
from notifier.line_client import send_line_message
from summarizer import summarize_text


def _article_key(article: Dict[str, str]) -> str:
    return article.get("id") or article.get("url") or ""


async def process_user_requests(
    requests: List[Dict[str, str]],
    articles: List[Dict[str, str]],
    processed_ids: Set[str],
    max_summary_chars: int,
) -> List[Dict[str, str]]:
    if not requests:
        return []

    remaining_requests: List[Dict[str, str]] = []
    for req in requests:
        query = req.get("query", "").strip()
        if not query:
            continue

        print(f"[INFO] リクエスト処理開始: {query}")
        matched_articles = filter_articles_by_query(articles, query)

        if not matched_articles:
            print(f"[INFO] リクエスト一致なし: {query}")
            continue

        sent_any = False
        for article in matched_articles[:5]:
            key = _article_key(article)
            if key and key in processed_ids:
                continue

            summary_input = f"{article.get('title', '')}\n{article.get('content', '')}"
            summary = await summarize_text(summary_input, max_chars=max_summary_chars)
            ok = await send_line_message(
                title=f"[検索:{query}] {article.get('title', '無題')}",
                summary=summary,
                url=article.get("url", ""),
            )
            if ok and key:
                processed_ids.add(key)
            sent_any = sent_any or ok

        if not sent_any:
            # 通知失敗時は再試行できるように残す
            remaining_requests.append(req)

    return remaining_requests
