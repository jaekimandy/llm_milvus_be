#!/usr/bin/env python3
"""
Test Milvus Vector Database

This script tests the Milvus vector database by performing
semantic searches on the stored documents.

Usage:
    python scripts/test_milvus.py
"""

import sys
import os
import asyncio
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.vector_store import vector_store
from agent.llm_client import llm_client


# Test queries
TEST_QUERIES = [
    "What is GaiA-ABiz?",
    "How does authentication work?",
    "Tell me about the AI agent",
    "What database is used for vectors?",
    "How is data encrypted?",
]


async def test_search(query: str, top_k: int = 3):
    """Test semantic search with a query"""
    print(f"\n🔍 Query: '{query}'")
    print("   " + "=" * 60)

    # Generate query embedding
    try:
        query_embedding = await llm_client.generate_embeddings(query)
        print(f"   ✓ Generated query embedding (dim: {len(query_embedding)})")
    except Exception as e:
        print(f"   ✗ Failed to generate embedding: {e}")
        return

    # Search
    try:
        results = vector_store.search(query_embedding, top_k=top_k)
        print(f"   ✓ Found {len(results)} results\n")

        for i, result in enumerate(results, 1):
            print(f"   Result {i}:")
            print(f"      Distance: {result['distance']:.4f}")
            print(f"      Text: {result['text'][:100]}...")

            metadata = json.loads(result['metadata'])
            print(f"      Source: {metadata.get('source', 'unknown')}")
            print(f"      Category: {metadata.get('category', 'unknown')}")
            print()

    except Exception as e:
        print(f"   ✗ Search failed: {e}")


async def test_milvus():
    """Run all tests"""
    print("🧪 Testing Milvus Vector Database")
    print()

    # Step 1: Connect
    print("1️⃣  Connecting to Milvus...")
    try:
        vector_store.connect()
        print("   ✓ Connected")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        print("\n💡 Make sure Milvus is running:")
        print("   docker-compose up -d milvus")
        sys.exit(1)

    # Step 2: Load collection
    print("\n2️⃣  Loading collection...")
    try:
        from pymilvus import Collection
        vector_store.collection = Collection(vector_store.collection_name)
        count = vector_store.collection.num_entities
        print(f"   ✓ Collection loaded: {vector_store.collection_name}")
        print(f"   ✓ Documents in collection: {count}")

        if count == 0:
            print("\n   ⚠️  No documents found!")
            print("   💡 Run: python scripts/add_sample_data.py first")
            sys.exit(1)

    except Exception as e:
        print(f"   ✗ Failed to load collection: {e}")
        print("\n💡 Run: python scripts/init_milvus.py first")
        sys.exit(1)

    # Step 3: Run test queries
    print("\n3️⃣  Running test queries...")
    print("   " + "=" * 60)

    for query in TEST_QUERIES:
        await test_search(query, top_k=3)

    print("=" * 64)
    print("\n✅ Milvus tests complete!")
    print("\n📊 Summary:")
    print(f"   - Total queries tested: {len(TEST_QUERIES)}")
    print(f"   - Documents in database: {count}")
    print(f"   - Embeddings provider: {llm_client.embeddings.__class__.__name__}")


if __name__ == "__main__":
    asyncio.run(test_milvus())
