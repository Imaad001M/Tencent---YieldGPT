"""Tencent VectorDB contract tests. All HTTP is mocked; no cloud bill or secret is needed."""
import json

import httpx
import pytest

from app.index import Index
from app.sources.base import SourceDoc
from app.vector_db import SemanticHit, TencentVectorDB, VectorDBUnavailable


def source(uid="confluence:CONF-1", text="PostgreSQL cutover needs a rollback checkpoint."):
    return SourceDoc(uid=uid, platform=uid.split(":", 1)[0], tenant="company-a",
        native_id=uid.split(":", 1)[1], container="engineering", title="Database migration",
        text=text, url="https://company.example/doc", version="1", updated_at=1790000000)


def test_tencent_upsert_search_and_delete_payloads_are_permission_filtered():
    requests = []
    def reply(request):
        body = json.loads(request.content)
        requests.append((request.url.path, body, request.headers))
        if request.url.path == "/document/search":
            return httpx.Response(200, json={"code": 0, "documents": [[
                {"uid": "confluence:CONF-1", "score": 0.91},
                {"uid": "confluence:CONF-1", "score": 0.88},
            ]]})
        return httpx.Response(200, json={"code": 0, "affectedCount": 1})
    client = httpx.Client(transport=httpx.MockTransport(reply))
    db = TencentVectorDB("https://vector.example", "secret", "brain", "chunks", client=client)
    db.upsert(source(), {"group:engineering", "user:jdoe"})
    hits = db.search("safe rollback plan", {"confluence"}, {"user:jdoe"}, {"confluence": 100})
    db.remove("confluence:CONF-1")

    assert hits == [SemanticHit("confluence:CONF-1", 0.91)]
    assert [path for path, _, _ in requests] == [
        "/document/delete", "/document/upsert", "/document/search", "/document/delete"]
    search = requests[2][1]["search"]
    assert search["embeddingItems"] == ["safe rollback plan"]
    assert 'acl_principals include ("user:jdoe")' in search["filter"]
    assert 'platform = "confluence"' in search["filter"]
    assert "updated_at >= 100" in search["filter"]
    assert requests[2][2]["authorization"] == "Bearer account=root&api_key=secret"


def test_bulk_crawl_deletes_and_upserts_multiple_sources_in_batches():
    requests = []
    def reply(request):
        requests.append((request.url.path, json.loads(request.content)))
        return httpx.Response(200, json={"code": 0})
    db = TencentVectorDB("https://vector.example", "secret", "brain", "chunks",
                         client=httpx.Client(transport=httpx.MockTransport(reply)))
    db.begin_bulk()
    db.upsert(source("confluence:A"), {"anyone"})
    db.upsert(source("jira:B"), {"group:engineering"})
    assert requests == []
    db.end_bulk()
    assert [path for path, _ in requests] == ["/document/delete", "/document/upsert"]
    assert 'uid in ("confluence:A", "jira:B")' == requests[0][1]["query"]["filter"]
    assert {row["uid"] for row in requests[1][1]["documents"]} == {"confluence:A", "jira:B"}


def test_local_acl_hint_rejects_bad_remote_hit_and_semantic_adds_authorized_candidate():
    class FakeVector:
        require_live = False
        def upsert(self, *_): pass
        def remove(self, *_): pass
        def search(self, *_):
            return [SemanticHit("confluence:HIDDEN", 1.0), SemanticHit("confluence:VISIBLE", .8)]
    index = Index(FakeVector())
    index.upsert(source("confluence:HIDDEN", "Secret acquisition planning."), {"group:security"})
    index.upsert(source("confluence:VISIBLE", "Rollback checkpoint procedure."), {"group:engineering"})
    hits = index.search("how can we reverse the deployment safely?", {"confluence"},
                        principals={"group:engineering"})
    assert [entry.doc.uid for _, entry in hits] == ["confluence:VISIBLE"]


def test_vector_failure_disables_stale_semantic_data_and_keeps_lexical_search():
    class BrokenVector:
        require_live = False
        def upsert(self, *_): raise VectorDBUnavailable("down")
        def remove(self, *_): raise VectorDBUnavailable("down")
        def search(self, *_): raise AssertionError("degraded backend must not be queried")
    index = Index(BrokenVector())
    index.upsert(source(), {"group:engineering"})
    assert index.mode == "lexical_fallback"
    assert index.vector_error == "VectorDBUnavailable"
    assert index.search("database migration", {"confluence"},
                        principals={"group:engineering"})


def test_required_vector_backend_fails_closed():
    class BrokenVector:
        require_live = True
        def upsert(self, *_): raise VectorDBUnavailable("down")
    index = Index(BrokenVector())
    with pytest.raises(VectorDBUnavailable):
        index.upsert(source(), {"group:engineering"})


def test_external_plain_http_requires_explicit_vpc_opt_in():
    with pytest.raises(ValueError, match="IB_VECTOR_ALLOW_HTTP"):
        TencentVectorDB("http://vector.example", "secret", "brain", "chunks")


def test_collection_schema_enables_managed_embedding_and_acl_filters():
    recorded = {}
    def reply(request):
        recorded.update(json.loads(request.content))
        return httpx.Response(200, json={"code": 0})
    db = TencentVectorDB("https://vector.example", "secret", "brain", "chunks",
                         client=httpx.Client(transport=httpx.MockTransport(reply)))
    db.create_collection("BAAI/bge-m3")
    assert recorded["embedding"] == {
        "field": "text", "vectorField": "vector", "model": "BAAI/bge-m3"}
    indexes = {row["fieldName"]: row for row in recorded["indexes"]}
    assert indexes["vector"]["indexType"] == "HNSW"
    assert indexes["acl_principals"]["fieldType"] == "array"
