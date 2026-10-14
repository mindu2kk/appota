from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


def _load_json(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    plain = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", plain).strip()


@dataclass(frozen=True)
class Decision:
    status: str
    answer: str
    citations: list[dict[str, str]]
    trace: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "answer": self.answer,
            "citations": self.citations,
            "trace": self.trace,
        }


class KnowledgeEngine:
    def __init__(self, data_dir: Path | None = None, today: date | None = None):
        data_dir = data_dir or ROOT / "data"
        self.users = {item["id"]: item for item in _load_json(data_dir / "users.json")}
        self.documents = _load_json(data_dir / "documents.json")
        self.today = today or date.today()

    def public_users(self) -> list[dict[str, str]]:
        return [
            {
                "id": user["id"],
                "name": user["name"],
                "company": user["company"],
                "department": user["department"],
                "role": user["role"],
            }
            for user in self.users.values()
        ]

    def ask(self, user_id: str, question: str) -> Decision:
        user = self.users.get(user_id)
        if not user:
            return self._refuse("Không xác định được danh tính người hỏi.", "UNKNOWN_USER")
        if not question or not question.strip():
            return self._refuse("Vui lòng nhập câu hỏi cần tra cứu.", "EMPTY_QUESTION")

        authorized = [doc for doc in self.documents if self._is_authorized(user, doc)]
        active = [doc for doc in authorized if self._is_active(doc)]
        scored = [(self._score(question, doc), doc) for doc in active]
        candidates = [doc for score, doc in scored if score > 0]

        trace = {
            "user_context": {
                "company": user["company"],
                "department": user["department"],
                "role": user["role"],
            },
            "authorized_active_documents_considered": len(active),
            "matched_documents": len(candidates),
            "policy": "authorization -> validity -> relevance -> specificity -> version",
        }
        if not candidates:
            return self._refuse(
                "Không tìm thấy tài liệu được phép truy cập và còn hiệu lực để trả lời câu hỏi này.",
                "INSUFFICIENT_EVIDENCE",
                trace,
            )

        top_intent = max(candidates, key=lambda doc: self._score(question, doc))["intent"]
        candidates = [doc for doc in candidates if doc["intent"] == top_intent]
        max_specificity = max(self._specificity(user, doc) for doc in candidates)
        candidates = [doc for doc in candidates if self._specificity(user, doc) == max_specificity]
        newest_version = max(self._version_key(doc["version"]) for doc in candidates)
        winners = [doc for doc in candidates if self._version_key(doc["version"]) == newest_version]

        distinct_answers = {doc["content"] for doc in winners}
        if len(distinct_answers) > 1:
            trace["resolution"] = "conflict_detected"
            trace["conflicting_sources"] = [self._citation(doc) for doc in winners]
            return self._refuse(
                "Có nhiều tài liệu cùng mức ưu tiên nhưng nội dung mâu thuẫn. Hệ thống từ chối kết luận; vui lòng liên hệ chủ sở hữu chính sách.",
                "CONFLICTING_EVIDENCE",
                trace,
                [self._citation(doc) for doc in winners],
            )

        chosen = winners[0]
        trace["resolution"] = "answered"
        trace["selected_scope"] = chosen["scope"]["level"]
        trace["selected_version"] = chosen["version"]
        return Decision(
            status="answered",
            answer=chosen["content"],
            citations=[self._citation(chosen)],
            trace=trace,
        )

    def _is_authorized(self, user: dict[str, Any], doc: dict[str, Any]) -> bool:
        access = doc["access"]
        if user["role"] not in access["roles"]:
            return False
        scope = doc["scope"]
        if scope["level"] == "group":
            return True
        if scope["level"] == "company":
            return scope["company"] == user["company"]
        return scope["company"] == user["company"] and scope["department"] == user["department"]

    def _is_active(self, doc: dict[str, Any]) -> bool:
        start = date.fromisoformat(doc["effective_from"])
        end = date.fromisoformat(doc["effective_to"]) if doc.get("effective_to") else None
        return start <= self.today and (end is None or self.today <= end)

    def _score(self, question: str, doc: dict[str, Any]) -> int:
        normalized = normalize(question)
        return sum(1 for keyword in doc["keywords"] if normalize(keyword) in normalized)

    @staticmethod
    def _specificity(user: dict[str, Any], doc: dict[str, Any]) -> int:
        return {"group": 1, "company": 2, "department": 3}[doc["scope"]["level"]]

    @staticmethod
    def _version_key(version: str) -> tuple[int, ...]:
        return tuple(int(part) for part in version.split("."))

    @staticmethod
    def _citation(doc: dict[str, Any]) -> dict[str, str]:
        return {
            "document_id": doc["id"],
            "title": doc["title"],
            "version": doc["version"],
            "effective_from": doc["effective_from"],
            "owner": doc["owner"],
        }

    @staticmethod
    def _refuse(
        message: str,
        reason: str,
        trace: dict[str, Any] | None = None,
        citations: list[dict[str, str]] | None = None,
    ) -> Decision:
        safe_trace = trace or {}
        safe_trace["reason"] = reason
        return Decision("refused", message, citations or [], safe_trace)
