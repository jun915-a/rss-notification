"""LINE Messaging API通知クライアント。"""

from __future__ import annotations

import asyncio
import os

import httpx


async def send_line_message(title: str, summary: str, url: str) -> bool:
    channel_token = os.getenv("LINE_CHANNEL_TOKEN")
    user_id = os.getenv("LINE_USER_ID")
    if not channel_token or not user_id:
        print("[WARN] LINE環境変数未設定のため通知をスキップ")
        return False

    message = f"【{title}】\n{summary}\n\n{url}"
    headers = {
        "Authorization": f"Bearer {channel_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message[:4900]}],
    }

    try:
        # レート制限回避のため送信間隔を確保
        await asyncio.sleep(1)
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post("https://api.line.me/v2/bot/message/push", json=payload, headers=headers)
            response.raise_for_status()
        print("[INFO] LINE送信成功")
        return True
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            print("[WARN] LINE 429検知: 今回はスキップ")
            return False
        print(f"[ERROR] LINE送信失敗(status={exc.response.status_code}): {exc}")
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] LINE送信失敗: {exc}")
        return False
