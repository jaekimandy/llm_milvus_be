#!/usr/bin/env python3
"""
Test RAG (Retrieval Augmented Generation) with Specific Information

This script tests the complete RAG pipeline:
1. Retrieves specific information from vector DB
2. Generates response using Claude AI with retrieved context
3. Verifies the LLM correctly uses the retrieved information

Usage:
    python scripts/test_vectordb_rag.py
"""

import sys
import os
import asyncio
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.vector_store import vector_store
from agent.llm_client import llm_client


async def test_rag_pipeline():
    """Test complete RAG pipeline with single query"""
    print("=" * 70)
    print("🤖 Testing RAG Pipeline")
    print("   (Retrieval Augmented Generation)")
    print("=" * 70)
    print()

    test_query = "Where did Jae Kim grow up?"
    print(f"📝 Query: '{test_query}'")
    print()

    # Step 1: Connect to Milvus
    print("1️⃣  Connecting to Milvus...")
    try:
        vector_store.connect()
        from pymilvus import Collection
        vector_store.collection = Collection(vector_store.collection_name)
        count = vector_store.collection.num_entities
        print(f"   ✓ Connected to Milvus")
        print(f"   ✓ Documents in database: {count}")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        sys.exit(1)

    # Step 2: Generate query embedding
    print("\n2️⃣  Generating query embedding...")
    try:
        query_embedding = await llm_client.generate_embeddings(test_query)
        print(f"   ✓ Generated embedding (dim: {len(query_embedding)})")
        print(f"   ✓ Provider: {llm_client.embeddings.__class__.__name__}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        sys.exit(1)

    # Step 3: Search vector database
    print("\n3️⃣  Searching vector database...")
    try:
        results = vector_store.search(query_embedding, top_k=3)
        print(f"   ✓ Found {len(results)} relevant documents\n")

        # Display results
        print("   📄 Retrieved Documents:")
        print("   " + "-" * 66)

        found_jae_kim = False
        for i, result in enumerate(results, 1):
            metadata = json.loads(result['metadata'])
            text_preview = result['text'][:70] + "..." if len(result['text']) > 70 else result['text']

            print(f"\n   Document {i}:")
            print(f"      Distance: {result['distance']:.4f}")
            print(f"      Source: {metadata.get('source', 'unknown')}")
            print(f"      Text: {text_preview}")

            # Check if this is our Jae Kim information
            if "Jae Kim" in result['text'] and "Jamsil" in result['text']:
                print(f"      🎯 Contains Jae Kim information!")
                found_jae_kim = True

        print("\n   " + "-" * 66)

        if not found_jae_kim:
            print("\n   ⚠️  Warning: Jae Kim information not in top 3 results")
            print("   💡 The test information might not have been added yet.")
            print("   💡 Run: python scripts/test_vectordb_specific.py first")
            return

    except Exception as e:
        print(f"   ✗ Search failed: {e}")
        sys.exit(1)

    # Step 4: Build context from retrieved documents
    print("\n4️⃣  Building context from retrieved documents...")
    context_parts = []
    for i, result in enumerate(results, 1):
        context_parts.append(f"[Document {i}]\n{result['text']}")

    context = "\n\n".join(context_parts)
    print(f"   ✓ Built context from {len(results)} documents")
    print(f"   ✓ Total context length: {len(context)} characters")

    # Step 5: Generate response with Claude AI
    print("\n5️⃣  Generating response with Claude AI...")
    try:
        prompt = f"""You are a helpful assistant. Answer the question based ONLY on the provided context.

Context:
{context}

Question: {test_query}

Instructions:
- Use only information from the context above
- If the context contains relevant information, provide a detailed answer
- If the context doesn't contain relevant information, say so
- Be specific and mention exact details from the context

Answer:"""

        print(f"   Sending prompt to Claude...")
        print(f"   Provider: {llm_client.provider}")

        # Format as message for the LLM client
        messages = [{"role": "user", "content": prompt}]
        response = await llm_client.generate_response(messages)
        print(f"   ✓ Response generated ({len(response)} characters)\n")

        # Display response
        print("   " + "=" * 66)
        print("   🤖 Claude's Response:")
        print("   " + "=" * 66)
        print()
        for line in response.split('\n'):
            print(f"   {line}")
        print()
        print("   " + "=" * 66)

    except Exception as e:
        print(f"   ✗ LLM generation failed: {e}")
        sys.exit(1)

    # Step 6: Verify response quality
    print("\n6️⃣  Verifying response quality...")

    key_terms = {
        "Jamsil": "Jamsil" in response,
        "New York": "New York" in response or "NY" in response,
        "Gyeongju": "Gyeongju" in response or "Gyeong" in response,
        "Kim": "Kim" in response
    }

    found_count = sum(key_terms.values())
    total_terms = len(key_terms)

    print(f"   Key information check:")
    for term, found in key_terms.items():
        status = "✓" if found else "✗"
        print(f"      {status} {term}: {'Found' if found else 'Not found'}")

    print()
    print(f"   Score: {found_count}/{total_terms} key terms found")

    if found_count >= 3:
        print("   ✅ EXCELLENT: Claude correctly used the retrieved context!")
    elif found_count >= 2:
        print("   ⚠️  GOOD: Claude used most of the context")
    elif found_count >= 1:
        print("   ⚠️  PARTIAL: Claude used some context")
    else:
        print("   ❌ POOR: Claude didn't use the retrieved context")

    # Final summary
    print("\n" + "=" * 70)
    print("📊 RAG Pipeline Test Summary")
    print("=" * 70)
    print(f"   ✓ Vector search: Working")
    print(f"   ✓ Retrieved Jae Kim info: {'Yes' if found_jae_kim else 'No'}")
    print(f"   ✓ Claude generation: Working")
    print(f"   ✓ Context usage: {found_count}/{total_terms} terms")
    print()

    if found_jae_kim and found_count >= 2:
        print("   ✅ RAG pipeline is working correctly!")
        print()
        print("   The system successfully:")
        print("   1. Stored specific information in vector DB")
        print("   2. Retrieved it via semantic search")
        print("   3. Used it to answer questions with Claude AI")
    else:
        print("   ⚠️  RAG pipeline needs improvement")

    print("=" * 70)


async def main():
    """Main test runner"""
    try:
        await test_rag_pipeline()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
