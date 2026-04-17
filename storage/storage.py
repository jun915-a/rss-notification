"""JSONベースの永続化層。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Set


class JsonStorage:
    def __init__(self, processed_path: str, requests_path: str) -> None:
        self.processed_path = Path(processed_path)
        self.requests_path = Path(requests_path)

    def _ensure_file(self, path: Path, default: Any) -> None:
        if not path.exists():
            path.write_text(json.dumps(default, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_json(self, path: Path, default: Any) -> Any:
        self._ensure_file(path, default)
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"[WARN] JSON破損を検知し初期化: {path}")
            return default
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] JSON読み込み失敗: {path} | {exc}")
            return default

    def _write_json(self, path: Path, data: Any) -> None:
        try:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] JSON書き込み失敗: {path} | {exc}")

    def load_processed_ids(self) -> Set[str]:
        data = self._read_json(self.processed_path, default=[])
        if not isinstance(data, list):
            return set()
        return {str(item) for item in data if item}

    def save_processed_ids(self, ids: Set[str]) -> None:
        self._write_json(self.processed_path, sorted(ids))

    def load_requests(self) -> List[Dict[str, str]]:
        data = self._read_json(self.requests_path, default=[])
        if not isinstance(data, list):
            return []
        normalized: List[Dict[str, str]] = []
        for item in data:
            if isinstance(item, dict) and item.get("query"):
                normalized.append(
                    {
                        "query": str(item.get("query", "")).strip(),
                        "timestamp": str(item.get("timestamp", "")),
                    }
                )
        return normalized

    def save_requests(self, requests: List[Dict[str, str]]) -> None:
        self._write_json(self.requests_path, requests)

    def add_request(self, query: str, timestamp: str) -> bool:
        """リクエストを追加する。重複queryは追加しない。"""
        normalized_query = query.strip()
        if not normalized_query:
            return False

        current = self.load_requests()
        if any(item.get("query", "").strip().lower() == normalized_query.lower() for item in current):
            return False

        current.append({"query": normalized_query, "timestamp": timestamp})
        self.save_requests(current)
        return True
