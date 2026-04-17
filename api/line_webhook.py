"""LINE Webhookを受けてrequests.jsonへ検索リクエストを登録するAPI。"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request

from storage.storage import JsonStorage

load_dotenv()

app = FastAPI(title="RSS Request Webhook API")
storage = JsonStorage("processed_articles.json", "requests.json")


def _is_valid_signature(raw_body: bytes, signature: str) -> bool:
    channel_secret = os.getenv("LINE_CHANNEL_SECRET")
    if not channel_secret:
        # 秘密鍵未設定時は検証をスキップ可能にしてローカル検証を容易にする
        return True
    digest = hmac.new(channel_secret.encode("utf-8"), raw_body, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(expected, signature)


def _extract_query_from_message(text: str) -> Optional[str]:
    msg = text.strip()
    if not msg:
        return None

    patterns = [
        r"(.+?)\s*な記事を探して",
        r"(.+?)\s*の記事を探して",
        r"(.+?)\s*を探して",
        r"(.+?)\s*記事",
    ]
    for pattern in patterns:
        match = re.search(pattern, msg, flags=re.IGNORECASE)
        if match:
            query = match.group(1).strip()
            if query:
                return query

    return msg


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook/line")
async def line_webhook(request: Request, x_line_signature: str = Header(default="")) -> dict[str, object]:
    raw = await request.body()
    if not _is_valid_signature(raw, x_line_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    events = payload.get("events", [])
    added = 0

    for event in events:
        if event.get("type") != "message":
            continue
        message = event.get("message", {})
        if message.get("type") != "text":
            continue
        query = _extract_query_from_message(message.get("text", ""))
        if not query:
            continue

        timestamp = datetime.now(timezone.utc).isoformat()
        if storage.add_request(query=query, timestamp=timestamp):
            added += 1
            print(f"[INFO] webhook request added: {query}")

    return {"ok": True, "added": added}
