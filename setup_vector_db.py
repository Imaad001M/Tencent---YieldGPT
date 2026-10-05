#!/usr/bin/env python3
"""Check or create the Tencent VectorDB collection configured in .env."""
import argparse

from app.vector_db import TencentVectorDB, VectorDBUnavailable


def main():
    parser = argparse.ArgumentParser(description="Provision the YieldGPT VectorDB collection")
    parser.add_argument("--create", action="store_true", help="create the configured collection")
    parser.add_argument("--model", default="BAAI/bge-m3", help="Tencent embedding model for a new collection")
    args = parser.parse_args()
    db = TencentVectorDB.from_env()
    if db is None:
        raise SystemExit("Set IB_VECTOR_PROVIDER=tencent and the IB_VECTOR_* settings first.")
    try:
        if args.create:
            db.create_collection(args.model)
            print("VectorDB collection created.")
        result = db.describe()
        collection = result.get("collection", result)
        embedding = collection.get("embedding", {}) if isinstance(collection, dict) else {}
        status = embedding.get("status", "unknown") if isinstance(embedding, dict) else "unknown"
        print(f"VectorDB connection succeeded; embedding status: {status}.")
    except (ValueError, VectorDBUnavailable) as error:
        raise SystemExit(str(error)) from None
    finally:
        db.close()


if __name__ == "__main__":
    main()
