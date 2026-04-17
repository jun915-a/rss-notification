"""記事フィルタリングモジュール。"""

from __future__ import annotations

from typing import Dict, List


def _contains_any_keyword(text: str, keywords: List[str]) -> bool:
    lower_text = (text or "").lower()
    return any(keyword.lower() in lower_text for keyword in keywords)


def matches_keywords(article: Dict[str, str], keywords: List[str]) -> bool:
    title = article.get("title", "")
    content = article.get("content", "")
    return _contains_any_keyword(title, keywords) or _contains_any_keyword(content, keywords)


def filter_articles_by_keywords(articles: List[Dict[str, str]], keywords: List[str]) -> List[Dict[str, str]]:
    filtered = [article for article in articles if matches_keywords(article, keywords)]
    print(f"[INFO] キーワードフィルタ: {len(filtered)}件 / {len(articles)}件")
    return filtered


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
