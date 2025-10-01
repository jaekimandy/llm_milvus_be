#!/usr/bin/env python3
"""
Test Vector Database with Specific Personal Information

This script tests the vector database by:
1. Adding very specific personal information not found on the internet
2. Querying for that information
3. Verifying RAG retrieval works correctly

Usage:
    python scripts/test_vectordb_specific.py
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.vector_store import vector_store
from agent.llm_client import llm_client


# Specific test information that doesn't exist on the internet
SPECIFIC_INFO = {
    "text": "Jae Kim grew up in Jamsil and New York. His last name is Kim and clan origin location is Gyeongju.",
    "metadata": {
        "source": "personal_info_test",
        "category": "biography",
        "person": "Jae Kim",
        "locations": ["Jamsil", "New York", "Gyeongju"],
        "test_id": "vectordb_specific_test_001",
        "timestamp": datetime.utcnow().isoformat()
    }
}

# Test queries that should retrieve this information
TEST_QUERIES = [
    "Where did Jae Kim grow up?",
    "What is Jae Kim's clan origin?",
    "Tell me about Jae Kim's background",
    "What is the clan origin location of Kim?",
    "Where is Jae Kim from?"
]


async def add_specific_info():
    """Add the specific personal information to vector database"""
    print("=" * 70)
    print("🧪 Testing Vector Database with Specific Information")
    print("=" * 70)
    print()

    print("📝 Test Information:")
    print(f"   Text: {SPECIFIC_INFO['text']}")
    print(f"   Source: {SPECIFIC_INFO['metadata']['source']}")
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

    # Step 2: Load collection
    print("\n2️⃣  Loading collection...")
    try:
        from pymilvus import Collection
        vector_store.collection = Collection(vector_store.collection_name)
        count_before = vector_store.collection.num_entities
        print(f"   ✓ Collection loaded: {vector_store.collection_name}")
        print(f"   ✓ Documents before insert: {count_before}")
    except Exception as e:
        print(f"   ✗ Failed to load collection: {e}")
        print("\n💡 Run: python scripts/init_milvus.py first")
        sys.exit(1)

    # Step 3: Generate embedding
    print("\n3️⃣  Generating embedding for specific information...")
    try:
        embedding = await llm_client.generate_embeddings(SPECIFIC_INFO['text'])
        print(f"   ✓ Generated embedding (dim: {len(embedding)})")
        print(f"   ✓ Embeddings provider: {llm_client.embeddings.__class__.__name__}")
    except Exception as e:
        print(f"   ✗ Failed to generate embedding: {e}")
        sys.exit(1)

    # Step 4: Insert into Milvus
    print("\n4️⃣  Inserting into Milvus...")
    try:
        metadata_str = json.dumps(SPECIFIC_INFO['metadata'])
        vector_store.insert(
            embeddings=[embedding],
            texts=[SPECIFIC_INFO['text']],
            metadata=[metadata_str]
        )
        print("   ✓ Inserted successfully")
    except Exception as e:
        print(f"   ✗ Insertion failed: {e}")
        sys.exit(1)

    # Step 5: Verify insertion
    print("\n5️⃣  Verifying insertion...")
    try:
        count_after = vector_store.collection.num_entities
        print(f"   ✓ Documents after insert: {count_after}")
        print(f"   ✓ New documents added: {count_after - count_before}")
    except Exception as e:
        print(f"   ✗ Verification failed: {e}")

    print("\n" + "=" * 70)
    print("✅ Specific information added to vector database!")
    print("=" * 70)


async def test_retrieval():
    """Test if we can retrieve the specific information"""
    print("\n\n")
    print("=" * 70)
    print("🔍 Testing Retrieval of Specific Information")
    print("=" * 70)
    print()

    successful_retrievals = 0
    failed_retrievals = 0

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n{'=' * 70}")
        print(f"Query {i}/{len(TEST_QUERIES)}: '{query}'")
        print("=" * 70)

        try:
            # Generate query embedding
            print("   Generating query embedding...")
            query_embedding = await llm_client.generate_embeddings(query)
            print(f"   ✓ Generated (dim: {len(query_embedding)})")

            # Search vector database
            print("   Searching vector database...")
            results = vector_store.search(query_embedding, top_k=3)
            print(f"   ✓ Found {len(results)} results\n")

            # Check if our specific information is in the results
            found_specific_info = False

            for j, result in enumerate(results, 1):
                metadata = json.loads(result['metadata'])
                is_our_test = metadata.get('test_id') == 'vectordb_specific_test_001'

                print(f"   Result {j}:")
                print(f"      Distance: {result['distance']:.4f}")
                print(f"      Text: {result['text'][:80]}...")
                print(f"      Source: {metadata.get('source', 'unknown')}")
                print(f"      Test Match: {'✓ YES' if is_our_test else '✗ No'}")
                print()

                if is_our_test:
                    found_specific_info = True

            if found_specific_info:
                print("   ✅ SUCCESS: Specific information retrieved!")
                successful_retrievals += 1
            else:
                print("   ⚠️  WARNING: Specific information NOT in top 3 results")
                failed_retrievals += 1

        except Exception as e:
            print(f"   ✗ Query failed: {e}")
            failed_retrievals += 1

    # Summary
    print("\n" + "=" * 70)
    print("📊 Retrieval Test Summary")
    print("=" * 70)
    print(f"   Total queries: {len(TEST_QUERIES)}")
    print(f"   Successful retrievals: {successful_retrievals}")
    print(f"   Failed retrievals: {failed_retrievals}")
    print(f"   Success rate: {(successful_retrievals/len(TEST_QUERIES)*100):.1f}%")

    if successful_retrievals == len(TEST_QUERIES):
        print("\n   ✅ Perfect! All queries retrieved the specific information!")
    elif successful_retrievals > 0:
        print("\n   ⚠️  Partial success. Some queries didn't retrieve the info.")
    else:
        print("\n   ❌ Failed! None of the queries retrieved the specific information.")

    print("=" * 70)

    return successful_retrievals, failed_retrievals


async def test_rag_with_llm():
    """Test RAG: Retrieve context and generate answer with LLM"""
    print("\n\n")
    print("=" * 70)
    print("🤖 Testing RAG (Retrieval + LLM Generation)")
    print("=" * 70)
    print()

    test_query = "Where did Jae Kim grow up?"

    print(f"Query: '{test_query}'\n")

    # Step 1: Retrieve context
    print("1️⃣  Retrieving context from vector database...")
    try:
        query_embedding = await llm_client.generate_embeddings(test_query)
        results = vector_store.search(query_embedding, top_k=3)
        print(f"   ✓ Retrieved {len(results)} documents\n")

        # Build context
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"Document {i}: {result['text']}")

        context = "\n".join(context_parts)
        print("   Retrieved Context:")
        print("   " + "-" * 66)
        for part in context_parts:
            print(f"   {part[:70]}...")
        print("   " + "-" * 66)

    except Exception as e:
        print(f"   ✗ Retrieval failed: {e}")
        return

    # Step 2: Generate response with LLM
    print("\n2️⃣  Generating response with LLM...")
    try:
        prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {test_query}

Answer:"""

        response = await llm_client.generate_response(prompt)
        print("   ✓ Response generated\n")

        print("   LLM Response:")
        print("   " + "=" * 66)
        print(f"   {response}")
        print("   " + "=" * 66)

        # Check if response mentions the key information
        key_terms = ["Jamsil", "New York", "Gyeongju"]
        found_terms = [term for term in key_terms if term.lower() in response.lower()]

        print(f"\n   Key terms found in response: {found_terms}")

        if len(found_terms) >= 2:
            print("   ✅ SUCCESS: LLM correctly used the retrieved context!")
        elif len(found_terms) >= 1:
            print("   ⚠️  PARTIAL: LLM used some context but not all details")
        else:
            print("   ❌ FAILED: LLM didn't use the retrieved context")

    except Exception as e:
        print(f"   ✗ LLM generation failed: {e}")

    print("\n" + "=" * 70)


async def cleanup_test_data():
    """Optional: Remove test data"""
    print("\n\n")
    print("=" * 70)
    print("🧹 Cleanup Options")
    print("=" * 70)
    print()
    print("The test data remains in the vector database.")
    print("To clean it up, you can:")
    print()
    print("Option 1: Delete by metadata filter (requires Milvus 2.3+)")
    print("Option 2: Recreate the collection:")
    print("   docker-compose exec api python scripts/init_milvus.py")
    print()
    print("For now, the test data will stay for future tests.")
    print()


async def main():
    """Run all tests"""
    try:
        # Add specific information
        await add_specific_info()

        # Wait a moment for Milvus to index
        print("\n⏳ Waiting 2 seconds for Milvus to index...")
        await asyncio.sleep(2)

        # Test retrieval
        successful, failed = await test_retrieval()

        # Test RAG with LLM
        if successful > 0:
            await test_rag_with_llm()

        # Cleanup info
        await cleanup_test_data()

        # Final result
        print("\n" + "=" * 70)
        print("🎉 Vector Database Test Complete!")
        print("=" * 70)

        if successful == len(TEST_QUERIES):
            print("\n✅ All tests passed! Vector database is working correctly.")
            sys.exit(0)
        elif successful > 0:
            print(f"\n⚠️  Partial success: {successful}/{len(TEST_QUERIES)} queries worked.")
            sys.exit(0)
        else:
            print("\n❌ Tests failed! Vector database may have issues.")
            sys.exit(1)

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
