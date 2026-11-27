from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from datetime import datetime


# Auth Schemas
class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


# Document Schemas
class DocumentResponse(BaseModel):
    id: int
    filename: str
    doc_type: str
    page_count: int
    chunk_count: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


# Topic Schemas
class SubtopicSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = ""
    exam_frequency: int = 0
    weightage_level: str = "Medium"

    class Config:
        from_attributes = True


class TopicHierarchyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = ""
    exam_frequency: int = 0
    weightage_level: str = "Medium"
    subtopics: List[SubtopicSchema] = []

    class Config:
        from_attributes = True


# Diagnostic Quiz Schemas
class QuizOption(BaseModel):
    id: str  # e.g., 'A', 'B', 'C', 'D'
    text: str


class QuizQuestionItem(BaseModel):
    id: Optional[int] = None
    question: str
    options: List[QuizOption]
    correct_answer: Optional[str] = None  # Hidden during quiz taking if needed
    citation: str  # e.g. "OS_Notes.pdf, Page 14"
    explanation: Optional[str] = None


class QuizGenerateRequest(BaseModel):
    topic_id: int
    question_count: int = 3


class QuizGenerateResponse(BaseModel):
    topic_id: int
    topic_name: str
    questions: List[QuizQuestionItem]


class StudentAnswer(BaseModel):
    question_index: int
    question_text: str
    options: List[QuizOption]
    student_answer: str
    correct_answer: str
    citation: str
    explanation: Optional[str] = None


class QuizSubmitRequest(BaseModel):
    topic_id: int
    answers: List[StudentAnswer]


class QuestionEvaluationResult(BaseModel):
    question: str
    student_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str
    citation: str


class QuizSubmitResponse(BaseModel):
    attempt_id: int
    topic_id: int
    topic_name: str
    score: int
    total_questions: int
    accuracy_pct: float
    status: str  # Weak, Medium, Strong
    evaluations: List[QuestionEvaluationResult]


# Gap Report Schemas
class TopicGapDetail(BaseModel):
    topic_id: int
    topic_name: str
    status: str  # Weak, Medium, Strong
    badge_color: str  # red, yellow, green
    accuracy_pct: float
    attempts_count: int
    exam_frequency: int
    weightage_level: str
    priority_score: float
    diagnostic_reason: str
    recommended_focus: str


class GapReportResponse(BaseModel):
    summary: Dict[str, int]  # {"weak": 2, "medium": 3, "strong": 1}
    overall_readiness_pct: float
    topics: List[TopicGapDetail]


# Revision Plan Schemas
class RevisionPlanRequest(BaseModel):
    target_days: int = 5
    daily_hours: float = 2.0


class StudyBlock(BaseModel):
    time_allocated_minutes: int
    topic_id: int
    topic_name: str
    status: str
    priority_score: float
    focus_objective: str
    recommended_source: str
    completed: bool = False


class DailyPlan(BaseModel):
    day: int
    day_title: str
    total_study_minutes: int
    blocks: List[StudyBlock]


class RevisionPlanResponse(BaseModel):
    plan_id: int
    target_days: int
    daily_hours: float
    total_study_hours: float
    schedule: List[DailyPlan]
    created_at: datetime
    updated_at: datetime


# Grounded Tutor / Explain Topic Schemas
class ExplainTopicRequest(BaseModel):
    topic_name: str
    user_query: Optional[str] = None


class GroundedCitation(BaseModel):
    filename: str
    page: int
    excerpt: str


class ExplainTopicResponse(BaseModel):
    topic_name: str
    explanation: str
    citations: List[GroundedCitation]
    grounded_in_material: bool


# Dashboard Schemas
class AttemptTrendItem(BaseModel):
    attempt_id: int
    topic_name: str
    accuracy_pct: float
    date: str


class DashboardMetricsResponse(BaseModel):
    total_documents: int
    total_topics: int
    quizzes_taken: int
    average_accuracy: float
    weak_count: int
    medium_count: int
    strong_count: int
    recent_attempts: List[AttemptTrendItem]
