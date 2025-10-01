#!/usr/bin/env python3
"""
Initialize Milvus Vector Database

This script:
1. Connects to Milvus
2. Creates the embeddings collection with correct dimensions
3. Creates indexes for efficient search

Usage:
    python scripts/init_milvus.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.vector_store import vector_store
from agent.llm_client import llm_client
from config.settings import settings
import asyncio


async def get_embedding_dimension():
    """Get the dimension of embeddings from the current provider"""
    print(f"📊 Detecting embedding dimensions for provider: {settings.EMBEDDINGS_PROVIDER}")

    # Generate a test embedding to get dimensions
    test_embedding = await llm_client.generate_embeddings("test")
    dim = len(test_embedding)

    print(f"✓ Embedding dimension: {dim}")
    return dim


def init_milvus():
    """Initialize Milvus collection"""
    print("🚀 Initializing Milvus Vector Database")
    print(f"   Host: {settings.MILVUS_HOST}")
    print(f"   Port: {settings.MILVUS_PORT}")
    print(f"   Collection: {settings.MILVUS_COLLECTION_NAME}")
    print()

    # Step 1: Connect to Milvus
    print("1️⃣  Connecting to Milvus...")
    try:
        vector_store.connect()
        print("   ✓ Connected successfully")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        print("\n💡 Make sure Milvus is running:")
        print("   docker-compose up -d milvus")
        sys.exit(1)

    # Step 2: Get embedding dimensions
    print("\n2️⃣  Detecting embedding dimensions...")
    try:
        dim = asyncio.run(get_embedding_dimension())
    except Exception as e:
        print(f"   ✗ Failed to get embedding dimensions: {e}")
        print("\n💡 Make sure your API keys are configured correctly in .env")
        sys.exit(1)

    # Step 3: Create collection
    print(f"\n3️⃣  Creating collection with dimension {dim}...")
    try:
        vector_store.create_collection(dim=dim)
        print("   ✓ Collection created successfully")
    except Exception as e:
        print(f"   ✗ Collection creation failed: {e}")
        sys.exit(1)

    # Step 4: Verify
    print("\n4️⃣  Verifying setup...")
    if vector_store.collection:
        print("   ✓ Collection is ready")
        print(f"   ✓ Collection name: {vector_store.collection.name}")
        print(f"   ✓ Collection schema: {vector_store.collection.schema}")
    else:
        print("   ✗ Collection not initialized")
        sys.exit(1)

    print("\n✅ Milvus initialization complete!")
    print("\n📝 Next steps:")
    print("   1. Add documents: python scripts/add_sample_data.py")
    print("   2. Test search: python scripts/test_milvus.py")


if __name__ == "__main__":
    init_milvus()
