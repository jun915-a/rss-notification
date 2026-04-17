"""記事フィルタリングモジュール。"""

from __future__ import annotations

from typing import Dict, List

NOISE_KEYWORDS = ["pr", "広告", "sponsored", "アフィリエイト"]
MAX_ARTICLES_PER_RUN = 1


def _build_search_text(article: Dict[str, str]) -> str:
    return f"{article.get('title', '')} {article.get('content', '')}".lower()


def matches_keywords(article: Dict[str, str], keywords: List[str]) -> bool:
    text = _build_search_text(article)
    return any(keyword.lower() in text for keyword in keywords)


def filter_articles_by_keywords(articles: List[Dict[str, str]], keywords: List[str]) -> List[Dict[str, str]]:
    filtered: List[Dict[str, str]] = []

    for article in articles:
        text = _build_search_text(article)

        if any(keyword.lower() in text for keyword in keywords):
            if not any(noise in text for noise in NOISE_KEYWORDS):
                filtered.append(article)

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
