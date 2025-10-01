from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from datetime import datetime
from common.database import Base


class APILog(Base):
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    method = Column(String, index=True)
    endpoint = Column(String, index=True)
    status_code = Column(Integer, index=True)
    duration = Column(Float)  # in seconds
    user_id = Column(Integer, index=True, nullable=True)
    request_body = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    agent_type = Column(String, index=True)
    user_id = Column(Integer, index=True)
    query = Column(Text)
    response = Column(Text)
    duration = Column(Float)  # in seconds
    status = Column(String, index=True)  # success, error, timeout
    error_message = Column(Text, nullable=True)
    tokens_used = Column(Integer, nullable=True)
