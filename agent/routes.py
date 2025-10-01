from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from common.database import get_db
from auth.security import get_current_active_user
from auth.models import User
from agent.models import AgentSession, AgentMessage, KnowledgeBase
from agent.schemas import (
    AgentQuery,
    AgentResponse,
    SessionCreate,
    SessionResponse,
    MessageResponse,
    KnowledgeBaseCreate,
    KnowledgeBaseResponse
)
from agent.graph_agent import create_agent
from agent.llm_client import llm_client
from agent.vector_store import vector_store
from monitoring.logger import get_logger
from monitoring.models import AgentLog
from datetime import datetime
import time
import json

router = APIRouter(prefix="/agent", tags=["AI Agent"])
logger = get_logger(__name__)


@router.post("/query", response_model=AgentResponse)
async def query_agent(
    query_data: AgentQuery,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Query the AI agent"""
    start_time = time.time()

    try:
        # Create or get session
        if query_data.session_id:
            session = db.query(AgentSession).filter(
                AgentSession.id == query_data.session_id,
                AgentSession.user_id == current_user.id
            ).first()
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            session = AgentSession(
                user_id=current_user.id,
                agent_type=query_data.agent_type
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        # Save user message
        user_message = AgentMessage(
            session_id=session.id,
            role="user",
            content=query_data.query
        )
        db.add(user_message)
        db.commit()

        # Create and run agent
        agent = create_agent(query_data.agent_type)
        result = await agent.run(query_data.query)

        # Save assistant message
        assistant_message = AgentMessage(
            session_id=session.id,
            role="assistant",
            content=result["response"],
            message_metadata={"retrieval_results": result.get("retrieval_results", [])}
        )
        db.add(assistant_message)
        db.commit()

        # Log agent activity
        duration = time.time() - start_time
        agent_log = AgentLog(
            agent_type=query_data.agent_type,
            user_id=current_user.id,
            query=query_data.query,
            response=result["response"],
            duration=duration,
            status="success"
        )
        db.add(agent_log)
        db.commit()

        logger.info(
            "agent_query_completed",
            agent_type=query_data.agent_type,
            user_id=current_user.id,
            duration=duration
        )

        return {
            "response": result["response"],
            "session_id": session.id,
            "context": result.get("context"),
            "retrieval_results": result.get("retrieval_results")
        }

    except Exception as e:
        duration = time.time() - start_time
        agent_log = AgentLog(
            agent_type=query_data.agent_type,
            user_id=current_user.id,
            query=query_data.query,
            response="",
            duration=duration,
            status="error",
            error_message=str(e)
        )
        db.add(agent_log)
        db.commit()

        logger.error(
            "agent_query_failed",
            agent_type=query_data.agent_type,
            user_id=current_user.id,
            error=str(e)
        )

        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new agent session"""
    session = AgentSession(
        user_id=current_user.id,
        agent_type=session_data.agent_type
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return session


@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's agent sessions"""
    sessions = db.query(AgentSession).filter(
        AgentSession.user_id == current_user.id
    ).order_by(AgentSession.created_at.desc()).all()

    return sessions


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get messages for a session"""
    session = db.query(AgentSession).filter(
        AgentSession.id == session_id,
        AgentSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(AgentMessage).filter(
        AgentMessage.session_id == session_id
    ).order_by(AgentMessage.created_at.asc()).all()

    return messages


@router.post("/knowledge-base", response_model=KnowledgeBaseResponse)
async def add_knowledge(
    knowledge_data: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add knowledge to the knowledge base and vector store"""
    try:
        # Generate embeddings
        embeddings = await llm_client.generate_embeddings(knowledge_data.content)

        # Store in vector database
        vector_store.connect()
        vector_store.create_collection()
        vector_store.insert(
            embeddings=[embeddings],
            texts=[knowledge_data.content],
            metadata=[json.dumps({
                "title": knowledge_data.title,
                "category": knowledge_data.category,
                "tags": knowledge_data.tags
            })]
        )

        # Store in database
        knowledge = KnowledgeBase(
            title=knowledge_data.title,
            content=knowledge_data.content,
            category=knowledge_data.category,
            tags=knowledge_data.tags
        )
        db.add(knowledge)
        db.commit()
        db.refresh(knowledge)

        return knowledge

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add knowledge: {str(e)}"
        )


@router.get("/knowledge-base", response_model=List[KnowledgeBaseResponse])
async def get_knowledge(
    category: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get knowledge base entries"""
    query = db.query(KnowledgeBase)

    if category:
        query = query.filter(KnowledgeBase.category == category)

    knowledge = query.order_by(KnowledgeBase.created_at.desc()).all()

    return knowledge
