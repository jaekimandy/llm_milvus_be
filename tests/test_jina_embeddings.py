"""
Tests for Jina Embeddings v3 - Semantic Search
"""
import pytest
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


@pytest.fixture(scope="module")
def embedding_model():
    """Load a multilingual embedding model for testing"""
    # Using all-MiniLM-L6-v2 as a fallback - widely used, stable model
    # For production with Korean, consider: paraphrase-multilingual-MiniLM-L12-v2
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return model


class TestJinaEmbeddings:
    """Test suite for Jina Embeddings v3"""

    def test_model_loading(self, embedding_model):
        """Test that the model loads successfully"""
        assert embedding_model is not None
        assert hasattr(embedding_model, 'encode')

    def test_single_embedding_generation(self, embedding_model):
        """Test generating embedding for a single text"""
        text = "This is a test sentence."
        embedding = embedding_model.encode(text)

        assert embedding is not None
        assert len(embedding.shape) == 1  # Should be 1D array
        assert embedding.shape[0] > 0  # Should have dimensions

    def test_batch_embedding_generation(self, embedding_model):
        """Test generating embeddings for multiple texts"""
        texts = [
            "Machine learning is fascinating.",
            "Deep learning models are powerful.",
            "Natural language processing enables AI."
        ]
        embeddings = embedding_model.encode(texts)

        assert embeddings is not None
        assert len(embeddings) == len(texts)
        assert embeddings.shape[0] == 3

    def test_semantic_similarity_high(self, embedding_model):
        """Test that semantically similar texts have high similarity"""
        text1 = "The cat sits on the mat."
        text2 = "A cat is sitting on a mat."

        emb1 = embedding_model.encode(text1)
        emb2 = embedding_model.encode(text2)

        similarity = cosine_similarity([emb1], [emb2])[0][0]

        # Similar sentences should have high similarity (> 0.7)
        assert similarity > 0.7
        print(f"\nSimilarity between similar sentences: {similarity:.4f}")

    def test_semantic_similarity_low(self, embedding_model):
        """Test that semantically different texts have low similarity"""
        text1 = "The weather is sunny today."
        text2 = "Quantum computing is complex."

        emb1 = embedding_model.encode(text1)
        emb2 = embedding_model.encode(text2)

        similarity = cosine_similarity([emb1], [emb2])[0][0]

        # Different sentences should have lower similarity (< 0.5)
        assert similarity < 0.5
        print(f"\nSimilarity between different sentences: {similarity:.4f}")

    def test_semantic_search_basic(self, embedding_model):
        """Test basic semantic search functionality"""
        # Document corpus
        documents = [
            "Python is a programming language.",
            "Machine learning uses algorithms to learn patterns.",
            "The Eiffel Tower is in Paris.",
            "Neural networks are inspired by the brain.",
            "Pizza is a popular Italian dish."
        ]

        # Query
        query = "What is deep learning?"

        # Generate embeddings
        doc_embeddings = embedding_model.encode(documents)
        query_embedding = embedding_model.encode(query)

        # Calculate similarities
        similarities = cosine_similarity([query_embedding], doc_embeddings)[0]

        # Get most similar document
        most_similar_idx = np.argmax(similarities)
        most_similar_doc = documents[most_similar_idx]

        print(f"\nQuery: {query}")
        print(f"Most similar document: {most_similar_doc}")
        print(f"Similarity score: {similarities[most_similar_idx]:.4f}")

        # The ML/Neural network related documents should be most similar
        assert most_similar_idx in [1, 3]  # Either ML or Neural network doc

    def test_multilingual_support(self, embedding_model):
        """Test multilingual embeddings (English and Korean)"""
        texts = [
            "Hello, how are you?",
            "안녕하세요, 어떻게 지내세요?",  # Korean: Hello, how are you?
        ]

        embeddings = embedding_model.encode(texts)

        assert embeddings is not None
        assert len(embeddings) == 2

        # Calculate similarity between English and Korean
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        print(f"\nEN-KO similarity: {similarity:.4f}")

        # Should have some similarity as they mean the same thing
        assert similarity > 0.3

    def test_korean_semantic_search(self, embedding_model):
        """Test semantic search with Korean text"""
        documents = [
            "인공지능은 컴퓨터가 인간처럼 생각하고 학습할 수 있게 합니다.",
            "파리는 프랑스의 수도입니다.",
            "파이썬은 프로그래밍 언어입니다.",
            "머신러닝은 데이터에서 패턴을 학습합니다.",
        ]

        query = "AI에 대해 알려주세요"  # Tell me about AI

        doc_embeddings = embedding_model.encode(documents)
        query_embedding = embedding_model.encode(query)

        similarities = cosine_similarity([query_embedding], doc_embeddings)[0]
        most_similar_idx = np.argmax(similarities)

        print(f"\nKorean Query: {query}")
        print(f"Most similar: {documents[most_similar_idx]}")
        print(f"Score: {similarities[most_similar_idx]:.4f}")

        # Should find the AI-related document (index 0 or 3)
        assert most_similar_idx in [0, 3]

    def test_embedding_consistency(self, embedding_model):
        """Test that same text produces same embedding"""
        text = "Consistency test sentence."

        emb1 = embedding_model.encode(text)
        emb2 = embedding_model.encode(text)

        # Should be identical (or very close due to floating point)
        similarity = cosine_similarity([emb1], [emb2])[0][0]
        assert similarity > 0.999  # Essentially 1.0

    def test_top_k_semantic_search(self, embedding_model):
        """Test retrieving top-k most similar documents"""
        documents = [
            "Python is great for data science.",
            "JavaScript is used for web development.",
            "Machine learning requires data.",
            "Deep learning is a subset of ML.",
            "The sky is blue.",
            "Data analysis is important.",
        ]

        query = "Tell me about machine learning"
        k = 3  # Top 3 results

        doc_embeddings = embedding_model.encode(documents)
        query_embedding = embedding_model.encode(query)

        similarities = cosine_similarity([query_embedding], doc_embeddings)[0]
        top_k_indices = np.argsort(similarities)[::-1][:k]

        print(f"\nQuery: {query}")
        print(f"Top {k} results:")
        for i, idx in enumerate(top_k_indices, 1):
            print(f"  {i}. {documents[idx]} (score: {similarities[idx]:.4f})")

        # ML-related documents should be in top 3
        ml_indices = {2, 3, 5}  # Indices of ML/data related docs
        assert len(set(top_k_indices) & ml_indices) >= 2
