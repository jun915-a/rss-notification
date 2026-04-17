"""記事フィルタリングモジュール。"""

from __future__ import annotations

import re
from typing import Dict, List

TARGET_KEYWORDS = [
    "AI",
    "人工知能",
    "machine learning",
    "Android",
    "Google Pixel",
]
MAX_ARTICLES_PER_RUN = 20


def _build_search_fields(article: Dict[str, str]) -> tuple[str, str, str]:
    title = (article.get("title", "") or "").lower()
    description = (article.get("content", "") or "").lower()
    combined = f"{title} {description}".strip()
    return title, description, combined


def matches_keywords(article: Dict[str, str], keywords: List[str]) -> bool:
    title, description, combined = _build_search_fields(article)

    for keyword in keywords:
        lowered = keyword.lower().strip()
        if not lowered:
            continue

        # 完全一致だけでなく、複合語はトークンのいずれか一致でも通す（OR強化）
        token_matches = [token for token in re.split(r"\s+", lowered) if token]
        if lowered in combined:
            return True
        if any(token in title or token in description for token in token_matches):
            return True
        # キーワードが長い場合は、部分一致の取りこぼしを減らす
        if len(lowered) >= 4 and (lowered[:4] in title or lowered[:4] in description):
            return True

    return False


def filter_articles_by_keywords(articles: List[Dict[str, str]], keywords: List[str]) -> List[Dict[str, str]]:
    # 設定値よりも安定運用向け固定キーワードを優先
    effective_keywords = TARGET_KEYWORDS if TARGET_KEYWORDS else keywords
    filtered = [article for article in articles if matches_keywords(article, effective_keywords)]
    limited = filtered[:MAX_ARTICLES_PER_RUN]
    print(f"[INFO] キーワードフィルタ: {len(limited)}件 / {len(articles)}件 (上限{MAX_ARTICLES_PER_RUN}件)")
    return limited


def filter_articles_by_query(articles: List[Dict[str, str]], query: str) -> List[Dict[str, str]]:
    tokens = [token.strip().lower() for token in query.split() if token.strip()]
    if not tokens:
        return []

    matched: List[Dict[str, str]] = []
    for article in articles:
        target = f"{article.get('title', '')} {article.get('content', '')}".lower()
        if all(token in target for token in tokens):
            matched.append(article)
    return matched
