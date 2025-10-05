"""
Tests for LangChain-based RAG (Retrieval Augmented Generation)
Testing semantic search and document retrieval with embeddings
"""
import pytest
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate


@pytest.fixture(scope="module")
def embedding_model():
    """Load multilingual embedding model for LangChain"""
    embeddings = HuggingFaceEmbeddings(
        model_name="paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={'device': 'cpu'}
    )
    return embeddings


@pytest.fixture(scope="module")
def sample_documents():
    """Create sample documents for testing"""
    docs = [
        Document(
            page_content="Python is a high-level programming language known for its simplicity and readability.",
            metadata={"source": "python_doc", "topic": "programming"}
        ),
        Document(
            page_content="Machine learning is a subset of artificial intelligence that enables computers to learn from data.",
            metadata={"source": "ml_doc", "topic": "ai"}
        ),
        Document(
            page_content="FastAPI is a modern web framework for building APIs with Python based on standard type hints.",
            metadata={"source": "fastapi_doc", "topic": "web"}
        ),
        Document(
            page_content="LangChain is a framework for developing applications powered by language models.",
            metadata={"source": "langchain_doc", "topic": "ai"}
        ),
        Document(
            page_content="인공지능은 인간의 학습능력과 추론능력을 컴퓨터로 구현하는 기술입니다.",
            metadata={"source": "ai_korean", "topic": "ai", "language": "ko"}
        ),
    ]
    return docs


@pytest.fixture(scope="module")
def vector_store(embedding_model, sample_documents):
    """Create FAISS vector store from sample documents"""
    vectorstore = FAISS.from_documents(sample_documents, embedding_model)
    return vectorstore


class TestLangChainRAG:
    """Test suite for LangChain RAG components"""

    def test_embedding_model_loading(self, embedding_model):
        """Test that embedding model loads successfully"""
        assert embedding_model is not None
        # Test embedding generation
        text = "Test sentence"
        embedding = embedding_model.embed_query(text)
        assert isinstance(embedding, list)
        assert len(embedding) > 0

    def test_document_creation(self, sample_documents):
        """Test document creation with metadata"""
        assert len(sample_documents) == 5
        assert all(isinstance(doc, Document) for doc in sample_documents)
        assert all(hasattr(doc, 'page_content') for doc in sample_documents)
        assert all(hasattr(doc, 'metadata') for doc in sample_documents)

    def test_vector_store_creation(self, vector_store):
        """Test FAISS vector store creation"""
        assert vector_store is not None
        # Check index size
        assert vector_store.index.ntotal == 5  # 5 documents

    def test_similarity_search(self, vector_store):
        """Test similarity search functionality"""
        query = "What is machine learning?"
        results = vector_store.similarity_search(query, k=3)

        assert len(results) <= 3
        assert all(isinstance(doc, Document) for doc in results)

        # First result should be ML-related
        print(f"\nQuery: {query}")
        print(f"Top result: {results[0].page_content}")
        assert "machine learning" in results[0].page_content.lower() or "artificial intelligence" in results[0].page_content.lower()

    def test_similarity_search_with_score(self, vector_store):
        """Test similarity search with relevance scores"""
        query = "Tell me about Python programming"
        results = vector_store.similarity_search_with_score(query, k=3)

        assert len(results) <= 3
        assert all(isinstance(result, tuple) for result in results)
        assert all(len(result) == 2 for result in results)

        doc, score = results[0]
        print(f"\nQuery: {query}")
        print(f"Top result: {doc.page_content}")
        print(f"Similarity score: {score:.4f}")

        # Python doc should be most relevant
        assert "python" in doc.page_content.lower()

    def test_korean_search(self, vector_store):
        """Test semantic search with Korean query"""
        query = "인공지능에 대해 알려주세요"  # Tell me about AI
        results = vector_store.similarity_search(query, k=2)

        assert len(results) > 0
        print(f"\nKorean Query: {query}")
        print(f"Top result: {results[0].page_content}")

        # Should find AI-related documents (Korean or English)
        top_content = results[0].page_content.lower()
        assert any(term in top_content for term in ["인공지능", "artificial intelligence", "machine learning"])

    def test_metadata_filtering(self, vector_store):
        """Test search with metadata filtering"""
        query = "AI framework"
        # Search only in AI topic documents
        results = vector_store.similarity_search(
            query,
            k=3,
            filter={"topic": "ai"}
        )

        assert len(results) > 0
        # All results should have topic "ai"
        for doc in results:
            assert doc.metadata.get("topic") == "ai"
            print(f"Found: {doc.page_content[:50]}... (topic: {doc.metadata.get('topic')})")

    def test_retriever_interface(self, vector_store):
        """Test LangChain retriever interface"""
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        assert retriever is not None

        query = "What is FastAPI?"
        docs = retriever.invoke(query)

        assert len(docs) > 0
        print(f"\nQuery: {query}")
        print(f"Retrieved {len(docs)} documents")
        print(f"Top result: {docs[0].page_content}")

    def test_mmr_search(self, vector_store):
        """Test Maximum Marginal Relevance (MMR) search for diversity"""
        query = "programming languages and AI"

        # MMR search balances relevance with diversity
        results = vector_store.max_marginal_relevance_search(
            query,
            k=3,
            fetch_k=5  # Fetch 5 candidates, return 3 diverse ones
        )

        assert len(results) <= 3
        print(f"\nMMR Search Query: {query}")
        for i, doc in enumerate(results, 1):
            print(f"{i}. {doc.page_content[:60]}...")

        # Should get diverse results (not all about same topic)
        topics = [doc.metadata.get("topic") for doc in results]
        assert len(set(topics)) > 1  # More than one topic

    def test_text_splitter(self):
        """Test document chunking with RecursiveCharacterTextSplitter"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=20,
            length_function=len
        )

        long_text = """
        LangChain is a framework for developing applications powered by language models.
        It provides tools and utilities for working with LLMs, including prompt management,
        chains for combining multiple components, and agents for autonomous decision-making.
        The framework supports various integrations with different LLM providers and
        vector stores for retrieval augmented generation.
        """

        chunks = splitter.split_text(long_text)

        assert len(chunks) > 1
        print(f"\nSplit text into {len(chunks)} chunks")
        for i, chunk in enumerate(chunks, 1):
            print(f"Chunk {i}: {len(chunk)} chars - {chunk[:50]}...")
            assert len(chunk) <= 100 + 20  # chunk_size + some overlap tolerance

    def test_add_documents_to_vectorstore(self, vector_store, embedding_model):
        """Test adding new documents to existing vector store"""
        initial_count = vector_store.index.ntotal

        new_docs = [
            Document(
                page_content="Docker is a platform for containerizing applications.",
                metadata={"source": "docker_doc", "topic": "devops"}
            ),
        ]

        vector_store.add_documents(new_docs)
        new_count = vector_store.index.ntotal

        assert new_count == initial_count + 1
        print(f"\nAdded documents: {initial_count} -> {new_count}")

        # Search for the new document
        results = vector_store.similarity_search("container platform", k=1)
        assert "docker" in results[0].page_content.lower()

    def test_save_and_load_vectorstore(self, vector_store, tmp_path):
        """Test saving and loading FAISS vector store"""
        # Save vector store
        save_path = str(tmp_path / "test_faiss_index")
        vector_store.save_local(save_path)

        # Load vector store
        embeddings = HuggingFaceEmbeddings(
            model_name="paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'}
        )
        loaded_store = FAISS.load_local(
            save_path,
            embeddings,
            allow_dangerous_deserialization=True
        )

        assert loaded_store is not None
        assert loaded_store.index.ntotal == vector_store.index.ntotal

        # Test search on loaded store
        results = loaded_store.similarity_search("Python", k=1)
        assert len(results) > 0
        print(f"\nLoaded vector store successfully with {loaded_store.index.ntotal} documents")
