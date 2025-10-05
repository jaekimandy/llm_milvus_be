"""
FastAPI Routes for RAG Functionality
Provides REST API endpoints for semantic search and document management
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from .rag_service import RAGService, QueryRequest, QueryResponse, DocumentRequest


# Create router
router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])

# Initialize RAG service (singleton)
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Dependency to get RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


class DocumentsRequest(BaseModel):
    """Request model for adding multiple documents"""
    documents: List[str]
    metadatas: Optional[List[Dict[str, Any]]] = None


class DocumentsResponse(BaseModel):
    """Response model for document operations"""
    success: bool
    message: str
    count: int


class StatsResponse(BaseModel):
    """Response model for statistics"""
    initialized: bool
    document_count: int
    embedding_model: Optional[str] = None


@router.post("/search", response_model=QueryResponse)
async def semantic_search(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Perform semantic search across documents

    Args:
        request: Query request with search parameters

    Returns:
        Search results with relevance scores
    """
    try:
        results = rag_service.semantic_search(
            query=request.query,
            k=request.k,
            filter_dict=request.filter
        )

        return QueryResponse(
            query=request.query,
            results=results,
            count=len(results)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/documents", response_model=DocumentsResponse)
async def add_documents(
    request: DocumentsRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Add documents to the vector store

    Args:
        request: Documents and optional metadata

    Returns:
        Success status and number of chunks added
    """
    try:
        count = rag_service.add_documents(
            documents=request.documents,
            metadatas=request.metadatas
        )

        return DocumentsResponse(
            success=True,
            message=f"Successfully added {len(request.documents)} documents ({count} chunks)",
            count=count
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add documents: {str(e)}"
        )


@router.post("/documents/single", response_model=DocumentsResponse)
async def add_single_document(
    request: DocumentRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Add a single document to the vector store

    Args:
        request: Document content and metadata

    Returns:
        Success status
    """
    try:
        count = rag_service.add_documents(
            documents=[request.content],
            metadatas=[request.metadata] if request.metadata else None
        )

        return DocumentsResponse(
            success=True,
            message=f"Successfully added document ({count} chunks)",
            count=count
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add document: {str(e)}"
        )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(rag_service: RAGService = Depends(get_rag_service)):
    """
    Get statistics about the RAG system

    Returns:
        System statistics including document count
    """
    try:
        stats = rag_service.get_stats()
        return StatsResponse(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": "RAG API",
        "version": "1.0.0"
    }
