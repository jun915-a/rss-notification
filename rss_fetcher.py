"""RSS取得モジュール。"""

from __future__ import annotations

import asyncio
import html
import re
from typing import Any, Dict, List

import feedparser


def _strip_html(text: str) -> str:
    clean = re.sub(r"<[^>]+>", " ", text or "")
    clean = html.unescape(clean)
    return re.sub(r"\s+", " ", clean).strip()


def _entry_to_article(entry: Dict[str, Any], source: str) -> Dict[str, str]:
    title = _strip_html(entry.get("title", ""))
    link = entry.get("link", "")
    article_id = entry.get("id") or link or entry.get("guid", "")

    content_text = ""
    if entry.get("summary"):
        content_text += f" {entry.get('summary')}"
    if entry.get("description"):
        content_text += f" {entry.get('description')}"
    if entry.get("content") and isinstance(entry["content"], list):
        for item in entry["content"]:
            if isinstance(item, dict):
                content_text += f" {item.get('value', '')}"

    return {
        "id": str(article_id),
        "title": title,
        "url": link,
        "content": _strip_html(content_text),
        "source": source,
    }


async def _parse_feed(url: str) -> List[Dict[str, str]]:
    # feedparserは同期関数なのでto_threadでイベントループをブロックしない
    parsed = await asyncio.to_thread(feedparser.parse, url)

    if parsed.bozo:
        bozo_exception = getattr(parsed, "bozo_exception", None)
        print(f"[WARN] RSS解析に失敗: {url} | {bozo_exception}")

    entries = parsed.get("entries", [])
    articles: List[Dict[str, str]] = []
    for entry in entries:
        try:
            article = _entry_to_article(entry, source=url)
            if article["url"] or article["id"]:
                articles.append(article)
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] 記事変換に失敗: {url} | {exc}")
    return articles


async def fetch_all_articles(feed_urls: List[str]) -> List[Dict[str, str]]:
    tasks = [_parse_feed(url) for url in feed_urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_articles: List[Dict[str, str]] = []
    for feed_url, result in zip(feed_urls, results):
        if isinstance(result, Exception):
            print(f"[ERROR] RSS取得失敗: {feed_url} | {result}")
            continue
        all_articles.extend(result)

    print(f"[INFO] RSS取得完了: {len(all_articles)}件")
    return all_articles
