"""RSS監視・要約・LINE通知のエントリーポイント。"""

from __future__ import annotations

import asyncio
import os
from typing import Dict, Set

import yaml
from dotenv import load_dotenv

from filter import filter_articles_by_keywords
from notifier.line_client import send_line_message
from request_handler import process_user_requests
from rss_fetcher import fetch_all_articles
from storage.storage import JsonStorage
from summarizer import summarize_text


def _load_config(path: str = "config.yaml") -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def _article_key(article: Dict[str, str]) -> str:
    return article.get("id") or article.get("url") or ""


async def _process_regular_articles(
    candidate_articles: list[dict[str, str]],
    processed_ids: Set[str],
    max_summary_chars: int,
) -> None:
    for article in candidate_articles:
        key = _article_key(article)
        if not key or key in processed_ids:
            continue

        try:
            summary_input = f"{article.get('title', '')}\n{article.get('content', '')}"
            summary = await summarize_text(summary_input, max_chars=max_summary_chars)

            # 🔽 追加：要約失敗ならスキップ（空送信防止）
            if not summary:
                print(f"[WARN] 要約失敗スキップ: {article.get('url')}")
                continue

            ok = await send_line_message(
                title=article.get("title", "無題"),
                summary=summary,
                url=article.get("url", ""),
            )

            if ok:
                processed_ids.add(key)

            # 🔽 追加：レート制限対策
            await asyncio.sleep(2)

        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] 記事処理失敗: {article.get('url')} | {exc}")


async def main() -> None:
    load_dotenv()
    storage = JsonStorage("processed_articles.json", "requests.json")

    try:
        config = _load_config()
        feed_urls = config.get("rss_feeds", [])
        keywords = config.get("filter_keywords", [])
        max_summary_chars = int(config.get("max_summary_chars", 200))
        if not isinstance(feed_urls, list) or not isinstance(keywords, list):
            raise ValueError("config.yamlの型が不正です")
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] 設定読み込み失敗: {exc}")
        return

    processed_ids = storage.load_processed_ids()
    requests = storage.load_requests()

    articles = await fetch_all_articles(feed_urls)
    filtered_articles = filter_articles_by_keywords(articles, keywords)

    # 🔽 追加：処理件数制限（超重要）
    MAX_ARTICLES_PER_RUN = 5
    filtered_articles = filtered_articles[:MAX_ARTICLES_PER_RUN]

    await _process_regular_articles(filtered_articles, processed_ids, max_summary_chars)

    remaining_requests = await process_user_requests(
        requests=requests,
        articles=articles,
        processed_ids=processed_ids,
        max_summary_chars=max_summary_chars,
    )

    storage.save_processed_ids(processed_ids)
    storage.save_requests(remaining_requests)
    print("[INFO] 全処理完了")


if __name__ == "__main__":
    # GitHub Actions上でも安全に実行できるようトップレベルでasyncio管理
    try:
        asyncio.run(main())
    except Exception as exc:  # noqa: BLE001
        print(f"[FATAL] 実行時例外: {exc}")
