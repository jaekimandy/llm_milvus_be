#!/usr/bin/env python3
"""
Add Sample Data to Milvus

This script adds sample documents to the Milvus vector database
for testing the RAG (Retrieval Augmented Generation) functionality.

Usage:
    python scripts/add_sample_data.py
"""

import sys
import os
import json
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.vector_store import vector_store
from agent.llm_client import llm_client


# Sample documents about the GaiA-ABiz project
SAMPLE_DOCUMENTS = [
    {
        "text": "GaiA-ABiz is a backend system for AI-powered business automation. It uses FastAPI, Claude AI, and Voyage AI embeddings.",
        "metadata": {"source": "project_overview", "category": "introduction"}
    },
    {
        "text": "The project supports multiple LLM providers: Anthropic Claude (recommended) and OpenAI GPT. Claude Sonnet 4 is the latest model.",
        "metadata": {"source": "llm_config", "category": "configuration"}
    },
    {
        "text": "For embeddings, the project uses Voyage AI (Anthropic's recommended partner) with the voyage-3 model. This provides superior quality for Claude workflows.",
        "metadata": {"source": "embeddings_config", "category": "configuration"}
    },
    {
        "text": "The system uses Milvus as its vector database for storing and searching document embeddings. It supports semantic search and RAG.",
        "metadata": {"source": "vector_db", "category": "architecture"}
    },
    {
        "text": "Authentication is handled via OAuth2.0 with JWT tokens. The system supports user registration, login, and token refresh.",
        "metadata": {"source": "auth_system", "category": "security"}
    },
    {
        "text": "The project includes comprehensive monitoring with Prometheus metrics and structured logging using structlog.",
        "metadata": {"source": "monitoring", "category": "observability"}
    },
    {
        "text": "Data encryption is implemented using Fernet symmetric encryption and AES-256. All sensitive data is encrypted at rest.",
        "metadata": {"source": "encryption", "category": "security"}
    },
    {
        "text": "The AI agent uses LangGraph to orchestrate workflows. It performs retrieval-augmented generation (RAG) by searching the vector database.",
        "metadata": {"source": "ai_agent", "category": "ai"}
    },
    {
        "text": "FastAPI provides the REST API with automatic OpenAPI documentation. Endpoints are available at /docs for Swagger UI.",
        "metadata": {"source": "api", "category": "api"}
    },
    {
        "text": "The project is containerized with Docker and can be deployed to Kubernetes. It includes docker-compose for local development.",
        "metadata": {"source": "deployment", "category": "devops"}
    },
]


async def add_sample_data():
    """Add sample documents to Milvus"""
    print("📚 Adding Sample Data to Milvus")
    print(f"   Documents to add: {len(SAMPLE_DOCUMENTS)}")
    print()

    # Step 1: Connect to Milvus
    print("1️⃣  Connecting to Milvus...")
    try:
        vector_store.connect()
        print("   ✓ Connected")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        print("\n💡 Run: python scripts/init_milvus.py first")
        sys.exit(1)

    # Step 2: Load collection
    print("\n2️⃣  Loading collection...")
    try:
        from pymilvus import Collection
        vector_store.collection = Collection(vector_store.collection_name)
        print(f"   ✓ Collection loaded: {vector_store.collection_name}")
    except Exception as e:
        print(f"   ✗ Failed to load collection: {e}")
        print("\n💡 Run: python scripts/init_milvus.py first")
        sys.exit(1)

    # Step 3: Generate embeddings
    print("\n3️⃣  Generating embeddings...")
    texts = [doc["text"] for doc in SAMPLE_DOCUMENTS]
    metadata_list = [json.dumps(doc["metadata"]) for doc in SAMPLE_DOCUMENTS]

    try:
        embeddings = await llm_client.generate_batch_embeddings(texts)
        print(f"   ✓ Generated {len(embeddings)} embeddings")
        print(f"   ✓ Embedding dimension: {len(embeddings[0])}")
    except Exception as e:
        print(f"   ✗ Failed to generate embeddings: {e}")
        print("\n💡 Check your API keys in .env")
        sys.exit(1)

    # Step 4: Insert into Milvus
    print("\n4️⃣  Inserting into Milvus...")
    try:
        vector_store.insert(
            embeddings=embeddings,
            texts=texts,
            metadata=metadata_list
        )
        print(f"   ✓ Inserted {len(texts)} documents")
    except Exception as e:
        print(f"   ✗ Insertion failed: {e}")
        sys.exit(1)

    # Step 5: Verify
    print("\n5️⃣  Verifying insertion...")
    try:
        vector_store.collection.load()
        count = vector_store.collection.num_entities
        print(f"   ✓ Total documents in collection: {count}")
    except Exception as e:
        print(f"   ✗ Verification failed: {e}")

    print("\n✅ Sample data added successfully!")
    print("\n📝 Next steps:")
    print("   Test search: python scripts/test_milvus.py")


if __name__ == "__main__":
    asyncio.run(add_sample_data())
