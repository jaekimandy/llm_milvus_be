"""
RAG Service for Semantic Search and Document Retrieval
Provides high-level RAG functionality using LangChain and vector stores
"""
from typing import List, Dict, Any, Optional
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel
import os


class QueryRequest(BaseModel):
    """Request model for semantic search"""
    query: str
    k: int = 3
    filter: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Response model for semantic search"""
    query: str
    results: List[Dict[str, Any]]
    count: int


class DocumentRequest(BaseModel):
    """Request model for adding documents"""
    content: str
    metadata: Optional[Dict[str, Any]] = None


class RAGService:
    """Service for RAG operations"""

    def __init__(
        self,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        vector_store_path: Optional[str] = None
    ):
        """
        Initialize RAG service

        Args:
            model_name: HuggingFace model name for embeddings
            vector_store_path: Path to saved vector store (optional)
        """
        # Store model name
        self.model_name = model_name

        # For Jina Embeddings v3, need trust_remote_code=True
        encode_kwargs = {'normalize_embeddings': True}
        if 'jina' in model_name.lower():
            model_kwargs = {'device': 'cpu', 'trust_remote_code': True}
        else:
            model_kwargs = {'device': 'cpu'}

        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

        # Initialize or load vector store
        if vector_store_path and os.path.exists(vector_store_path):
            self.vectorstore = FAISS.load_local(
                vector_store_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            # Start with empty vector store (will be populated later)
            self.vectorstore = None

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> int:
        """
        Add documents to the vector store

        Args:
            documents: List of document texts
            metadatas: Optional list of metadata dictionaries

        Returns:
            Number of documents added
        """
        # Create Document objects
        docs = []
        for i, text in enumerate(documents):
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            # Split long documents into chunks
            chunks = self.text_splitter.split_text(text)
            for j, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_index"] = j
                chunk_metadata["total_chunks"] = len(chunks)
                docs.append(Document(page_content=chunk, metadata=chunk_metadata))

        # Add to vector store
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(docs, self.embeddings)
        else:
            self.vectorstore.add_documents(docs)

        return len(docs)

    def semantic_search(
        self,
        query: str,
        k: int = 3,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search

        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filter

        Returns:
            List of search results with content, metadata, and scores
        """
        if self.vectorstore is None:
            return []

        # Perform search with scores
        if filter_dict:
            results = self.vectorstore.similarity_search_with_score(
                query,
                k=k,
                filter=filter_dict
            )
        else:
            results = self.vectorstore.similarity_search_with_score(query, k=k)

        # Format results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            })

        return formatted_results

    def get_retriever(self, search_type: str = "similarity", k: int = 3):
        """
        Get a LangChain retriever interface

        Args:
            search_type: Type of search ("similarity" or "mmr")
            k: Number of results

        Returns:
            LangChain Retriever
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Add documents first.")

        return self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs={"k": k}
        )

    def save(self, path: str):
        """Save vector store to disk"""
        if self.vectorstore is None:
            raise ValueError("No vector store to save")

        self.vectorstore.save_local(path)

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        # Get embedding dimension from embeddings client
        try:
            test_embedding = self.embeddings.embed_query("test")
            embedding_dimension = len(test_embedding)
        except:
            embedding_dimension = 0

        if self.vectorstore is None:
            return {
                "initialized": False,
                "document_count": 0,
                "embedding_model": self.model_name,
                "embedding_dimension": embedding_dimension
            }

        return {
            "initialized": True,
            "document_count": self.vectorstore.index.ntotal,
            "embedding_model": self.model_name,
            "embedding_dimension": embedding_dimension
        }
