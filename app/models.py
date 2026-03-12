from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class WorkflowStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    MANUAL_REVIEW = "MANUAL_REVIEW"

class WorkflowRequest(Base):

    __tablename__ = "workflow_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    idempotency_key = Column(String, unique=True, nullable=False, index=True)
    workflow_type = Column(String, nullable=False)
    status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.PENDING)

    input_data = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    audit_logs = relationship("AuditLog", back_populates="request")

class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("workflow_requests.id"), nullable=False)

    step_name = Column(String, nullable=False)
    action_type = Column(String, nullable=False)

    input_snapshot = Column(JSON)
    decision_outcome = Column(String)
    reasoning = Column(String)

    status = Column(String)
    error_message = Column(Text, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow)

    request = relationship("WorkflowRequest", back_populates="audit_logs")