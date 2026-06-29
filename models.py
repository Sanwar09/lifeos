"""LifeOS AI — SQLAlchemy Database Models"""
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Enum
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import uuid


def generate_id():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_id)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    avatar_url = Column(String)
    timezone = Column(String, default="Asia/Kolkata")
    preferences = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=generate_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="pending")  # pending, in_progress, completed, overdue, cancelled
    priority = Column(String, default="medium")  # critical, high, medium, low
    due_date = Column(DateTime)
    project_id = Column(String)
    goal_id = Column(String, ForeignKey("goals.id"))
    source = Column(String, default="manual")  # manual, agent, document, workflow
    source_agent = Column(String)
    tags = Column(JSON, default=[])
    estimated_minutes = Column(Integer)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="tasks")
    goal = relationship("Goal", back_populates="tasks", foreign_keys=[goal_id])


class Goal(Base):
    __tablename__ = "goals"

    id = Column(String, primary_key=True, default=generate_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, default="personal")
    status = Column(String, default="active")  # active, completed, paused, abandoned
    target_date = Column(DateTime)
    progress_percent = Column(Float, default=0.0)
    milestones = Column(JSON, default=[])
    ai_suggestions = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="goals")
    tasks = relationship("Task", back_populates="goal", foreign_keys=[Task.goal_id])


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String)
    file_type = Column(String)  # pdf, image, text, invoice, syllabus, bill, notes
    file_path = Column(String)
    file_size_bytes = Column(Integer)
    summary = Column(Text)
    extracted_text = Column(Text)
    key_dates = Column(JSON, default=[])
    key_amounts = Column(JSON, default=[])
    action_items = Column(JSON, default=[])
    tags = Column(JSON, default=[])
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    embedding_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="documents")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String, primary_key=True, default=generate_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    category = Column(String, default="other")
    type = Column(String, default="expense")  # expense, income, subscription, bill
    date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    is_paid = Column(Boolean, default=False)
    source_document_id = Column(String, ForeignKey("documents.id"))
    notes = Column(Text)
    vendor = Column(String)
    recurring = Column(Boolean, default=False)
    recurring_period = Column(String)  # daily, weekly, monthly, yearly
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="expenses")


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(String, primary_key=True, default=generate_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    all_day = Column(Boolean, default=False)
    type = Column(String, default="personal")
    location = Column(String)
    attendees = Column(JSON, default=[])
    source = Column(String, default="manual")
    source_agent = Column(String)
    reminder_minutes = Column(Integer, default=30)
    status = Column(String, default="scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)


class Memory(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, default=generate_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String, default="fact")
    importance = Column(String, default="medium")
    source = Column(String, default="user")
    source_agent = Column(String)
    related_entity_type = Column(String)
    related_entity_id = Column(String)
    embedding_id = Column(String)
    expires_at = Column(DateTime)
    accessed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="memories")


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(String, primary_key=True, default=generate_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    notes = Column(Text)
    summary = Column(Text)
    attendees = Column(JSON, default=[])
    decisions = Column(JSON, default=[])
    action_items = Column(JSON, default=[])
    date = Column(DateTime)
    document_id = Column(String, ForeignKey("documents.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=generate_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, default="info")  # info, warning, success, agent_update
    source_agent = Column(String)
    is_read = Column(Boolean, default=False)
    action_url = Column(String)
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
