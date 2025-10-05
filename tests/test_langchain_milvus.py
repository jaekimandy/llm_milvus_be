"""
Tests for LangChain + Milvus Vector Store Integration
Milvus is the production-grade vector database for RAG
"""
import pytest
from langchain_milvus import Milvus
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from pymilvus import connections, utility, Collection
import time


@pytest.fixture(scope="module")
def embedding_model():
    """Load multilingual embedding model"""
    embeddings = HuggingFaceEmbeddings(
        model_name="paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={'device': 'cpu'}
    )
    return embeddings


@pytest.fixture(scope="module")
def milvus_connection():
    """Connect to Milvus (standalone or lite)"""
    try:
        # Try connecting to Milvus standalone
        connections.connect(
            alias="default",
            host="localhost",
            port="19530"
        )
        yield "standalone"
        connections.disconnect("default")
    except Exception as e:
        # Fallback to Milvus Lite (embedded)
        pytest.skip(f"Milvus server not available: {e}. Start with: docker-compose up -d milvus")


@pytest.fixture(scope="module")
def sample_documents():
    """Create sample documents for testing"""
    docs = [
        Document(
            page_content="LangChain is a framework for developing LLM applications with composable components.",
            metadata={"source": "langchain_doc", "category": "framework", "language": "en"}
        ),
        Document(
            page_content="Milvus is an open-source vector database built for scalable similarity search and AI applications.",
            metadata={"source": "milvus_doc", "category": "database", "language": "en"}
        ),
        Document(
            page_content="RAG combines retrieval and generation to create more accurate AI responses.",
            metadata={"source": "rag_doc", "category": "concept", "language": "en"}
        ),
        Document(
            page_content="벡터 데이터베이스는 임베딩 벡터를 효율적으로 저장하고 검색합니다.",
            metadata={"source": "vector_db_korean", "category": "database", "language": "ko"}
        ),
        Document(
            page_content="SK Hynix is a global semiconductor company specializing in memory solutions.",
            metadata={"source": "skhynix_doc", "category": "company", "language": "en"}
        ),
    ]
    return docs


@pytest.fixture(scope="module")
def vector_store(milvus_connection, embedding_model, sample_documents):
    """Create Milvus vector store"""
    collection_name = f"test_collection_{int(time.time())}"

    # Create Milvus vector store
    vectorstore = Milvus.from_documents(
        documents=sample_documents,
        embedding=embedding_model,
        collection_name=collection_name,
        connection_args={"host": "localhost", "port": "19530"}
    )

    yield vectorstore

    # Cleanup: drop collection after tests
    try:
        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)
    except:
        pass


class TestLangChainMilvus:
    """Test suite for LangChain + Milvus integration"""

    def test_milvus_connection(self, milvus_connection):
        """Test Milvus server connection"""
        assert milvus_connection == "standalone"

        # List collections
        collections = utility.list_collections()
        print(f"\nConnected to Milvus. Collections: {collections}")
        assert isinstance(collections, list)

    def test_vector_store_creation(self, vector_store):
        """Test Milvus vector store creation"""
        assert vector_store is not None
        assert vector_store.col is not None

        # Check collection stats
        collection = vector_store.col
        stats = collection.num_entities
        print(f"\nCollection has {stats} entities")
        assert stats == 5

    def test_similarity_search(self, vector_store):
        """Test similarity search in Milvus"""
        query = "What is RAG?"
        results = vector_store.similarity_search(query, k=3)

        assert len(results) > 0
        assert len(results) <= 3

        print(f"\nQuery: {query}")
        print(f"Top result: {results[0].page_content}")

        # Should find RAG-related document
        assert any("RAG" in doc.page_content or "retrieval" in doc.page_content.lower()
                  for doc in results)

    def test_similarity_search_with_score(self, vector_store):
        """Test similarity search with relevance scores"""
        query = "vector database for embeddings"
        results = vector_store.similarity_search_with_score(query, k=3)

        assert len(results) > 0
        assert all(isinstance(r, tuple) and len(r) == 2 for r in results)

        doc, score = results[0]
        print(f"\nQuery: {query}")
        print(f"Top result: {doc.page_content}")
        print(f"Distance: {score:.4f}")

        # Lower distance = higher similarity
        # Should find Milvus or vector database related doc
        assert "Milvus" in doc.page_content or "vector" in doc.page_content.lower() or "벡터" in doc.page_content

    def test_korean_search(self, vector_store):
        """Test Korean language semantic search"""
        query = "벡터 검색에 대해 알려주세요"
        results = vector_store.similarity_search(query, k=2)

        assert len(results) > 0
        print(f"\nKorean query: {query}")
        print(f"Top result: {results[0].page_content}")

        # Should find Korean or database-related documents
        top_result = results[0].page_content.lower()
        assert "벡터" in results[0].page_content or "vector" in top_result or "database" in top_result

    def test_metadata_filtering(self, vector_store):
        """Test filtering by metadata"""
        query = "technology"

        # Search only in database category
        expr = 'category == "database"'
        results = vector_store.similarity_search(
            query,
            k=3,
            expr=expr
        )

        assert len(results) > 0
        print(f"\nFiltered search (category=database): {len(results)} results")

        # All results should be database category
        for doc in results:
            print(f"  - {doc.page_content[:60]}... (category: {doc.metadata.get('category')})")
            assert doc.metadata.get("category") == "database"

    def test_add_documents(self, vector_store):
        """Test adding new documents to existing collection"""
        initial_count = vector_store.col.num_entities

        new_docs = [
            Document(
                page_content="LangGraph enables building stateful multi-agent applications.",
                metadata={"source": "langgraph_doc", "category": "framework"}
            ),
            Document(
                page_content="FastAPI is a modern web framework for building Python APIs.",
                metadata={"source": "fastapi_doc", "category": "framework"}
            ),
        ]

        # Add documents
        vector_store.add_documents(new_docs)

        # Flush to ensure data is persisted
        vector_store.col.flush()

        new_count = vector_store.col.num_entities
        print(f"\nAdded documents: {initial_count} -> {new_count}")
        assert new_count == initial_count + 2

    def test_retriever_interface(self, vector_store):
        """Test LangChain retriever interface with Milvus"""
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        assert retriever is not None

        query = "memory solutions company"
        docs = retriever.invoke(query)

        assert len(docs) > 0
        print(f"\nRetriever query: {query}")
        print(f"Retrieved {len(docs)} documents")
        print(f"Top: {docs[0].page_content[:80]}...")

    def test_mmr_search(self, vector_store):
        """Test Maximum Marginal Relevance search for diverse results"""
        query = "AI and databases"

        # MMR search for diversity
        results = vector_store.max_marginal_relevance_search(
            query,
            k=3,
            fetch_k=5,  # Fetch 5, return 3 diverse
            lambda_mult=0.5  # Balance relevance vs diversity
        )

        assert len(results) > 0
        print(f"\nMMR Search: {query}")
        for i, doc in enumerate(results, 1):
            print(f"{i}. {doc.page_content[:60]}... (category: {doc.metadata.get('category')})")

        # Should have diverse categories
        categories = [doc.metadata.get("category") for doc in results]
        assert len(set(categories)) > 1

    def test_hybrid_search_with_filter(self, vector_store):
        """Test combining similarity search with metadata filters"""
        query = "framework"

        # Search only English documents
        expr = 'language == "en"'
        results = vector_store.similarity_search(
            query,
            k=5,
            expr=expr
        )

        print(f"\nHybrid search (English only): {len(results)} results")
        for doc in results:
            assert doc.metadata.get("language") == "en"
            print(f"  - {doc.page_content[:50]}...")

    def test_delete_by_filter(self, vector_store):
        """Test deleting documents by metadata filter"""
        initial_count = vector_store.col.num_entities

        # Add a test document
        test_doc = [Document(
            page_content="This is a temporary test document.",
            metadata={"source": "test", "category": "temp", "delete": True}
        )]
        vector_store.add_documents(test_doc)
        vector_store.col.flush()

        count_after_add = vector_store.col.num_entities
        assert count_after_add == initial_count + 1

        # Delete by filter
        expr = 'delete == True'
        vector_store.col.delete(expr)
        vector_store.col.flush()

        final_count = vector_store.col.num_entities
        print(f"\nDelete test: {initial_count} -> {count_after_add} -> {final_count}")
        assert final_count == initial_count

    def test_collection_info(self, vector_store):
        """Test retrieving collection information"""
        collection = vector_store.col

        # Get schema
        schema = collection.schema
        print(f"\nCollection: {collection.name}")
        print(f"Description: {collection.description}")
        print(f"Fields: {[field.name for field in schema.fields]}")

        # Get stats
        stats = collection.num_entities
        print(f"Total entities: {stats}")

        assert stats > 0
        assert collection.name.startswith("test_collection_")
