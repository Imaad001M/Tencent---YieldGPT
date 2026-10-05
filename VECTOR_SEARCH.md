# Tencent VectorDB hybrid retrieval

The project now has a real Tencent Cloud VectorDB HTTP adapter in `app/vector_db.py`. It sends bounded, overlapping text chunks to a Base collection configured with Tencent's managed Embedding feature, batches full-crawl writes, searches by raw question text, and fuses those semantic candidates with the existing exact/lexical candidates. The original lexical path remains available for local demos and as a safe fallback.

## Why this does not bypass permissions

VectorDB is a candidate generator, never an authorization service.

1. Every vector row stores the source document UID, platform, update time, and the connector's ACL-hint principals.
2. Searches use VectorDB filter indexes for the asker's principals, requested platforms, and time window.
3. Returned UIDs must also exist in the current local index and pass its ACL-hint check. VectorDB text is never used as answer evidence.
4. The source connector performs a live native permission check, reads through the asker's identity where supported, and checks permission and version again before release.
5. Semantic hits supplement all lexical hits; there is no shared pre-authorization top-k that lets a hidden semantic result remove a visible lexical result.
6. Any indexing failure disables semantic search for that process, preventing stale remote vectors from being used. `IB_VECTOR_REQUIRE_LIVE=1` makes a VectorDB failure stop startup or the affected operation instead of falling back.

ACL hints can be broader than the platform's real permission decision. They reduce the candidate set but never grant access.

## Tencent setup

Create a Tencent Cloud VectorDB **Base** instance and a database, then copy `.env.example` to `.env` and set:

```dotenv
IB_VECTOR_PROVIDER=tencent
IB_VECTOR_BASE_URL=https://YOUR_INSTANCE_HOST:PORT
IB_VECTOR_API_KEY=YOUR_REAL_KEY
IB_VECTOR_ACCOUNT=root
IB_VECTOR_DATABASE=internal_brain
IB_VECTOR_COLLECTION=knowledge_chunks
IB_VECTOR_REQUIRE_LIVE=1
```

Tencent's private VPC endpoints may use HTTP. For a private endpoint only, set `IB_VECTOR_ALLOW_HTTP=1`. HTTPS is required by default. Keep the API key in `.env` or the deployment secret store; never add it to the JSON Slack configuration or source control. `root` is convenient for one-time collection creation. For the running app, create a narrower Tencent account with document read/write rights and set `IB_VECTOR_ACCOUNT` to that account.

Create the collection once:

```sh
python scripts/setup_vector_db.py --create --model BAAI/bge-m3
```

If the collection already exists, check it without changing schema:

```sh
python scripts/setup_vector_db.py
```

The collection schema uses an HNSW/COSINE vector index and filter indexes for `uid`, `platform`, `updated_at`, and the string-array field `acl_principals`. `text` is the managed embedding input and `vector` is its generated output. Startup never creates or alters cloud schema automatically.

## Local and failure modes

- `IB_VECTOR_PROVIDER=lexical`: zero-credential local mode.
- `IB_VECTOR_PROVIDER=tencent`, `IB_VECTOR_REQUIRE_LIVE=0`: hybrid mode with lexical fallback if cloud indexing/search fails.
- `IB_VECTOR_PROVIDER=tencent`, `IB_VECTOR_REQUIRE_LIVE=1`: deployment mode; fail rather than silently lose the required vector capability.

The signed-in UI exposes the active retrieval mode returned by `/api/session`. The Tencent adapter and filter behavior are tested with mocked HTTP. A real Tencent instance was not available in this development session, so the team must run the setup check and live evaluation with approved credentials before claiming a live deployment.

Official references:

- HTTP prerequisites and authentication: https://cloud.tencent.com/document/product/1709/98666
- Managed Embedding setup: https://cloud.tencent.com/document/product/1709/98681
- Text similarity search: https://cloud.tencent.com/document/product/1709/95123
- Filter expressions, including array `include`: https://cloud.tencent.com/document/product/1709/112947
