"""
Aurora Database Models
SQLAlchemy models for Aurora-X system
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SynthesisTask(Base):
    """Synthesis task tracking."""

    __tablename__ = "synthesis_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    prompt = Column(Text, nullable=False)
    framework = Column(String(50))  # 'flask', 'function', etc.
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    result_data = Column(JSON)
    files_generated = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


class ConversationHistory(Base):
    """Chat conversation history."""

    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_id = Column(String(100), index=True)
    role = Column(String(20))  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    extra_data = Column(JSON)  # Changed from 'metadata' (reserved word)
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemMetric(Base):
    """System metrics for monitoring."""

    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_type = Column(String(50), index=True)  # 'cpu', 'memory', 'disk', 'service'
    component = Column(String(100))  # 'backend', 'frontend', 'chat', etc.
    value = Column(Float)
    unit = Column(String(20))  # '%', 'GB', 'MB', 'count'
    status = Column(String(20))  # 'healthy', 'warning', 'critical'
    extra_data = Column(JSON)  # Changed from 'metadata' (reserved word)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class Alert(Base):
    """System alerts and notifications."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    severity = Column(String(20), index=True)  # 'info', 'warning', 'critical'
    component = Column(String(100), index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    value = Column(Float)
    threshold = Column(Float)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class AuditLog(Base):
    """Audit log for tracking system events."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    status = Column(String(20))  # 'success', 'failure'
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# Export all models
__all__ = [
    "Base",
    "User",
    "SynthesisTask",
    "ConversationHistory",
    "SystemMetric",
    "Alert",
    "AuditLog",
]
