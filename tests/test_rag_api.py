"""
Tests for RAG FastAPI Endpoints
Tests the REST API for semantic search and document management
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from agent.api_routes import router, _rag_service
from agent.rag_service import RAGService


@pytest.fixture(scope="module")
def app():
    """Create FastAPI test application"""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture(scope="module")
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def reset_rag_service():
    """Reset RAG service before each test"""
    global _rag_service
    import agent.api_routes as api_routes_module
    api_routes_module._rag_service = None
    yield
    api_routes_module._rag_service = None


class TestRAGAPI:
    """Test suite for RAG API endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/rag/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "RAG API"
        print(f"\nHealth check: {data}")

    def test_get_stats_empty(self, client):
        """Test getting stats from empty vector store"""
        response = client.get("/api/v1/rag/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["initialized"] == False
        assert data["document_count"] == 0
        print(f"\nEmpty stats: {data}")

    def test_add_single_document(self, client):
        """Test adding a single document"""
        request_data = {
            "content": "LangChain is a framework for building LLM applications.",
            "metadata": {"source": "test", "category": "framework"}
        }

        response = client.post("/api/v1/rag/documents/single", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["count"] >= 1
        print(f"\nAdd single document: {data}")

    def test_add_multiple_documents(self, client):
        """Test adding multiple documents"""
        request_data = {
            "documents": [
                "SK Hynix produces memory semiconductors.",
                "GaiA is an AI platform for enterprises.",
                "FastAPI is a modern web framework for Python."
            ],
            "metadatas": [
                {"source": "doc1", "category": "company"},
                {"source": "doc2", "category": "ai"},
                {"source": "doc3", "category": "framework"}
            ]
        }

        response = client.post("/api/v1/rag/documents", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["count"] >= 3
        print(f"\nAdd multiple documents: {data}")

    def test_semantic_search_basic(self, client):
        """Test basic semantic search"""
        # First add documents
        add_request = {
            "documents": [
                "Python is a programming language used for AI and web development.",
                "Machine learning enables computers to learn from data.",
                "The weather today is sunny and warm."
            ]
        }
        client.post("/api/v1/rag/documents", json=add_request)

        # Perform search
        search_request = {
            "query": "What is machine learning?",
            "k": 2
        }

        response = client.post("/api/v1/rag/search", json=search_request)

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "What is machine learning?"
        assert data["count"] > 0
        assert len(data["results"]) <= 2

        print(f"\nSearch query: {data['query']}")
        print(f"Results count: {data['count']}")
        for i, result in enumerate(data["results"], 1):
            print(f"  {i}. {result['content'][:60]}... (score: {result['score']:.4f})")

        # Verify ML-related document is in top results
        top_result = data["results"][0]["content"].lower()
        assert "machine learning" in top_result or "learn" in top_result

    def test_semantic_search_korean(self, client):
        """Test semantic search with Korean content"""
        # Add Korean documents
        add_request = {
            "documents": [
                "인공지능은 컴퓨터가 인간처럼 학습하는 기술입니다.",
                "Python은 프로그래밍 언어입니다.",
                "날씨가 좋습니다."
            ],
            "metadatas": [
                {"language": "ko"},
                {"language": "ko"},
                {"language": "ko"}
            ]
        }
        client.post("/api/v1/rag/documents", json=add_request)

        # Search in Korean
        search_request = {
            "query": "AI 기술에 대해 알려주세요",
            "k": 2
        }

        response = client.post("/api/v1/rag/search", json=search_request)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] > 0
        print(f"\nKorean search: {data['results'][0]['content'][:50]}...")

    def test_stats_after_adding_documents(self, client):
        """Test stats after adding documents"""
        # Add documents
        add_request = {
            "documents": [
                "Document 1 content here.",
                "Document 2 content here.",
                "Document 3 content here."
            ]
        }
        client.post("/api/v1/rag/documents", json=add_request)

        # Get stats
        response = client.get("/api/v1/rag/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["initialized"] == True
        assert data["document_count"] > 0
        assert "embedding_model" in data
        print(f"\nStats after adding docs: {data}")

    def test_search_with_empty_store(self, client):
        """Test search when no documents are added"""
        search_request = {
            "query": "test query",
            "k": 3
        }

        response = client.post("/api/v1/rag/search", json=search_request)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []
        print("\nSearch on empty store returns empty results")

    def test_search_with_k_parameter(self, client):
        """Test search with different k values"""
        # Add documents
        add_request = {
            "documents": [f"Document number {i}" for i in range(10)]
        }
        client.post("/api/v1/rag/documents", json=add_request)

        # Search with k=3
        search_request = {"query": "document", "k": 3}
        response = client.post("/api/v1/rag/search", json=search_request)
        data = response.json()
        assert len(data["results"]) <= 3

        # Search with k=5
        search_request = {"query": "document", "k": 5}
        response = client.post("/api/v1/rag/search", json=search_request)
        data = response.json()
        assert len(data["results"]) <= 5

        print(f"\nSearch with k=3: {len(data['results'])} results")

    def test_concurrent_document_additions(self, client):
        """Test adding documents in multiple requests"""
        # First batch
        response1 = client.post("/api/v1/rag/documents", json={
            "documents": ["Doc 1", "Doc 2"]
        })
        assert response1.status_code == 200

        # Second batch
        response2 = client.post("/api/v1/rag/documents", json={
            "documents": ["Doc 3", "Doc 4"]
        })
        assert response2.status_code == 200

        # Check stats
        stats = client.get("/api/v1/rag/stats").json()
        assert stats["document_count"] >= 4
        print(f"\nTotal documents after batches: {stats['document_count']}")

    def test_error_handling_invalid_request(self, client):
        """Test error handling for invalid requests"""
        # Missing required field
        invalid_request = {"k": 3}  # Missing 'query'

        response = client.post("/api/v1/rag/search", json=invalid_request)

        assert response.status_code == 422  # Validation error
        print("\nInvalid request properly rejected")
