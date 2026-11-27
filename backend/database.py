import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "study_app.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)  # For demo simplicity or hashed
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    topics = relationship("Topic", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    revision_plans = relationship("RevisionPlan", back_populates="user", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    doc_type = Column(String(50), nullable=False)  # 'syllabus', 'notes', 'past_paper'
    file_path = Column(String(500), nullable=False)
    page_count = Column(Integer, default=1)
    chunk_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="documents")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    parent_topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    description = Column(Text, default="")
    exam_frequency = Column(Integer, default=0)  # Count of past paper questions linked
    weightage_level = Column(String(50), default="Medium")  # High, Medium, Low
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="topics")
    subtopics = relationship("Topic", backref="parent_topic", remote_side=[id])
    quiz_attempts = relationship("QuizAttempt", back_populates="topic")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    score = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    accuracy_pct = Column(Float, default=0.0)
    status = Column(String(50), default="Weak")  # Weak, Medium, Strong
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="quiz_attempts")
    topic = relationship("Topic", back_populates="quiz_attempts")
    questions = relationship("QuizQuestion", back_populates="attempt", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    options_json = Column(Text, nullable=False)  # JSON serialized list of options
    correct_answer = Column(String(255), nullable=False)
    student_answer = Column(String(255), nullable=True)
    is_correct = Column(Boolean, default=False)
    explanation = Column(Text, default="")
    citation = Column(String(255), default="")  # e.g., 'OS_Notes.pdf, Page 12'

    attempt = relationship("QuizAttempt", back_populates="questions")


class RevisionPlan(Base):
    __tablename__ = "revision_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_days = Column(Integer, default=5)
    daily_hours = Column(Float, default=2.0)
    plan_json = Column(Text, nullable=False)  # JSON serialized schedule structure
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="revision_plans")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
