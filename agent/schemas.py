from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class AgentQuery(BaseModel):
    query: str
    agent_type: str = "general"
    session_id: Optional[int] = None


class AgentResponse(BaseModel):
    response: str
    session_id: int
    context: Optional[str] = None
    retrieval_results: Optional[List[Dict[str, Any]]] = None


class SessionCreate(BaseModel):
    agent_type: str = "general"


class SessionResponse(BaseModel):
    id: int
    user_id: int
    agent_type: str
    created_at: datetime
    status: str

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeBaseCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class KnowledgeBaseResponse(BaseModel):
    id: int
    title: str
    content: str
    category: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True
