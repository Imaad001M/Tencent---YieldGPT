"""Optional Tencent Cloud VectorDB backend for permission-aware semantic retrieval.

VectorDB proposes candidates; it never authorizes them.  The local index checks the
stored ACL hint and Brain still performs the connector's live native permission
check before source text can enter the model context.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from .sources.base import SourceDoc

_SAFE_FILTER_VALUE = re.compile(r"^[A-Za-z0-9_@.:/-]{1,256}$")
_SAFE_NAME = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


class VectorDBUnavailable(RuntimeError):
    """A fixed-text VectorDB failure that never includes provider response data."""


def _filter_string(value: str) -> str:
    if not _SAFE_FILTER_VALUE.fullmatch(value):
        raise ValueError("VectorDB filter value contains unsupported characters")
    return json.dumps(value, ensure_ascii=True)


def _validated_base_url(value: str, allow_http: bool) -> str:
    parsed = urlparse(value.strip())
    if (parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment or parsed.path not in {"", "/"}):
        raise ValueError("IB_VECTOR_BASE_URL must be an HTTP(S) origin without a path")
    if parsed.scheme == "http" and not allow_http and parsed.hostname != "localhost":
        raise ValueError("Plain HTTP VectorDB endpoints require IB_VECTOR_ALLOW_HTTP=1")
    return value.rstrip("/")


def _chunks(doc: SourceDoc, size: int = 1800, overlap: int = 220) -> list[str]:
    """Create bounded, overlapping semantic units without changing source evidence."""
    text = re.sub(r"\s+", " ", doc.text).strip()
    if not text:
        return [doc.title[:size]]
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = max(text.rfind(". ", start + size // 2, end),
                           text.rfind("; ", start + size // 2, end),
                           text.rfind(" ", start + size // 2, end))
            if boundary > start:
                end = boundary + 1
        body = text[start:end].strip()
        if body:
            chunks.append((doc.title + "\n" + body)[: size + len(doc.title) + 1])
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks[:128]


@dataclass(frozen=True)
class SemanticHit:
    uid: str
    score: float


class TencentVectorDB:
    """Small HTTP client for a Tencent Base collection configured with Embedding."""

    def __init__(self, base_url: str, api_key: str, database: str, collection: str, *,
                 timeout: float = 5.0, limit: int = 200, allow_http: bool = False,
                 require_live: bool = False, account: str = "root",
                 client: httpx.Client | None = None):
        if not api_key or api_key.upper().startswith(("YOUR_", "PLACEHOLDER", "REPLACE")):
            raise ValueError("IB_VECTOR_API_KEY is missing or still a placeholder")
        if (not _SAFE_NAME.fullmatch(database) or not _SAFE_NAME.fullmatch(collection)
                or not _SAFE_NAME.fullmatch(account)):
            raise ValueError("VectorDB account, database, or collection name is invalid")
        if not 1 <= limit <= 1000:
            raise ValueError("IB_VECTOR_LIMIT must be between 1 and 1000")
        self.base_url = _validated_base_url(base_url, allow_http)
        self.database, self.collection = database, collection
        self.limit, self.require_live = limit, require_live
        self._headers = {
            "Authorization": f"Bearer account={account}&api_key={api_key}",
            "Content-Type": "application/json",
        }
        self.client = client or httpx.Client(timeout=timeout, follow_redirects=False)
        self._bulk = False
        self._pending: dict[str, tuple[SourceDoc, set[str]] | None] = {}

    @classmethod
    def from_env(cls) -> "TencentVectorDB | None":
        provider = os.getenv("IB_VECTOR_PROVIDER", "lexical").strip().casefold()
        if provider in {"", "lexical", "none"}:
            return None
        if provider not in {"tencent", "tencent_vectordb"}:
            raise ValueError("IB_VECTOR_PROVIDER must be lexical or tencent")
        return cls(
            os.getenv("IB_VECTOR_BASE_URL", ""),
            os.getenv("IB_VECTOR_API_KEY", ""),
            os.getenv("IB_VECTOR_DATABASE", "internal_brain"),
            os.getenv("IB_VECTOR_COLLECTION", "knowledge_chunks"),
            timeout=float(os.getenv("IB_VECTOR_TIMEOUT_S", "5")),
            limit=int(os.getenv("IB_VECTOR_LIMIT", "200")),
            allow_http=os.getenv("IB_VECTOR_ALLOW_HTTP", "0") == "1",
            require_live=os.getenv("IB_VECTOR_REQUIRE_LIVE", "0") == "1",
            account=os.getenv("IB_VECTOR_ACCOUNT", "root"),
        )

    def _post(self, path: str, payload: dict) -> dict:
        try:
            response = self.client.post(self.base_url + path, headers=self._headers, json=payload)
            response.raise_for_status()
            result = response.json()
            if not isinstance(result, dict) or result.get("code") != 0:
                raise VectorDBUnavailable("VectorDB rejected the operation")
            return result
        except VectorDBUnavailable:
            raise
        except Exception as error:
            raise VectorDBUnavailable(f"VectorDB request failed ({type(error).__name__})") from None

    def describe(self) -> dict:
        return self._post("/collection/describe", {
            "database": self.database, "collection": self.collection,
        })

    def create_collection(self, model: str = "BAAI/bge-m3") -> dict:
        """Provision the collection schema. Run explicitly; startup never mutates schema."""
        if not _SAFE_FILTER_VALUE.fullmatch(model):
            raise ValueError("Embedding model name is invalid")
        return self._post("/collection/create", {
            "database": self.database,
            "collection": self.collection,
            "replicaNum": 1,
            "shardNum": 1,
            "description": "Permission-filtered YieldGPT knowledge chunks",
            "embedding": {"field": "text", "vectorField": "vector", "model": model},
            "indexes": [
                {"fieldName": "id", "fieldType": "string", "indexType": "primaryKey"},
                {"fieldName": "vector", "fieldType": "vector", "indexType": "HNSW",
                 "metricType": "COSINE", "params": {"M": 16, "efConstruction": 200}},
                {"fieldName": "uid", "fieldType": "string", "indexType": "filter"},
                {"fieldName": "platform", "fieldType": "string", "indexType": "filter"},
                {"fieldName": "updated_at", "fieldType": "uint64", "indexType": "filter"},
                {"fieldName": "acl_principals", "fieldType": "array", "indexType": "filter"},
            ],
        })

    def begin_bulk(self) -> None:
        self._bulk = True

    def end_bulk(self) -> None:
        try:
            self._flush()
        finally:
            self._bulk = False

    def _delete_uids(self, uids: list[str]) -> None:
        if not uids:
            return
        values = ", ".join(_filter_string(uid) for uid in uids)
        self._post("/document/delete", {
            "database": self.database,
            "collection": self.collection,
            "query": {"filter": f"uid in ({values})", "limit": 16384},
        })

    @staticmethod
    def _documents(doc: SourceDoc, acl_hint: set[str]) -> list[dict]:
        prefix = hashlib.sha256(doc.uid.encode("utf-8")).hexdigest()[:40]
        return [{
            "id": f"{prefix}-{number:03d}",
            "text": text,
            "uid": doc.uid,
            "platform": doc.platform,
            "updated_at": max(0, int(doc.updated_at)),
            "acl_principals": sorted(acl_hint),
        } for number, text in enumerate(_chunks(doc))]

    def _flush(self) -> None:
        if not self._pending:
            return
        pending, self._pending = self._pending, {}
        uids = list(pending)
        # Clear all previous chunks in one filtered operation. Reinsert in bounded
        # batches so a full enterprise crawl does not make one request per page.
        self._delete_uids(uids)
        documents = []
        for item in pending.values():
            if item is not None:
                documents.extend(self._documents(*item))
        for start in range(0, len(documents), 100):
            self._post("/document/upsert", {
                "database": self.database,
                "collection": self.collection,
                "buildIndex": True,
                "documents": documents[start:start + 100],
            })

    def upsert(self, doc: SourceDoc, acl_hint: set[str]) -> None:
        self._pending[doc.uid] = (doc, set(acl_hint))
        if not self._bulk or len(self._pending) >= 50:
            self._flush()

    def remove(self, uid: str) -> None:
        self._pending[uid] = None
        if not self._bulk or len(self._pending) >= 50:
            self._flush()

    def search(self, query: str, platforms: set[str], principals: set[str],
               since: dict[str, float] | None = None) -> list[SemanticHit]:
        safe_principals = sorted(p for p in principals if _SAFE_FILTER_VALUE.fullmatch(p))
        safe_platforms = sorted(p for p in platforms if _SAFE_FILTER_VALUE.fullmatch(p))
        if not query.strip() or not safe_principals or not safe_platforms:
            return []
        acl = ", ".join(_filter_string(p) for p in safe_principals)
        platform_terms = []
        for platform in safe_platforms:
            term = f"platform = {_filter_string(platform)}"
            lower = (since or {}).get(platform, float("-inf"))
            if math.isfinite(lower):
                term = f"({term} and updated_at >= {max(0, int(lower))})"
            platform_terms.append(term)
        filter_expression = f"acl_principals include ({acl}) and ({' or '.join(platform_terms)})"
        result = self._post("/document/search", {
            "database": self.database,
            "collection": self.collection,
            "readConsistency": "strongConsistency",
            "search": {
                "embeddingItems": [query],
                "limit": self.limit,
                "params": {"ef": max(200, self.limit)},
                "retrieveVector": False,
                "filter": filter_expression,
                "outputFields": ["uid", "platform", "updated_at"],
            },
        })
        rows = result.get("documents", [])
        if rows and isinstance(rows[0], list):
            rows = rows[0]
        best: dict[str, float] = {}
        for row in rows if isinstance(rows, list) else []:
            if not isinstance(row, dict) or not isinstance(row.get("uid"), str):
                continue
            try:
                score = float(row.get("score", 0.0))
            except (TypeError, ValueError):
                continue
            best[row["uid"]] = max(score, best.get(row["uid"], float("-inf")))
        return [SemanticHit(uid, score) for uid, score in
                sorted(best.items(), key=lambda item: (-item[1], item[0]))]

    def close(self) -> None:
        self.client.close()
