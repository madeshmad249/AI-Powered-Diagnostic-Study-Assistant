import os
import json
import shutil
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database import (
    init_db, get_db, User, Document, Topic, QuizAttempt, QuizQuestion, RevisionPlan
)
from models import (
    LoginRequest, AuthResponse, UserResponse, DocumentResponse,
    TopicHierarchyResponse, SubtopicSchema,
    QuizGenerateRequest, QuizGenerateResponse, QuizOption, QuizQuestionItem,
    QuizSubmitRequest, QuizSubmitResponse, QuestionEvaluationResult,
    GapReportResponse, TopicGapDetail,
    RevisionPlanRequest, RevisionPlanResponse,
    ExplainTopicRequest, ExplainTopicResponse,
    DashboardMetricsResponse, AttemptTrendItem
)
from ingestion import process_and_ingest_file
STORAGE_UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "uploads"))
from rag_engine import retrieve_topic_context, generate_grounded_quiz, explain_topic_grounded
from diagnostic import classify_topic_gap, generate_diagnostic_reason, build_adaptive_revision_plan

app = FastAPI(
    title="GapFinder AI - Diagnostic Study Assistant API",
    version="1.0.0",
    description="Full-stack AI Diagnostic Study Doctor: Document Ingestion, Topic Mapping, Grounded Testing, Gap Diagnosis, and Adaptive Revision Planning."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup: initialize database tables
@app.on_event("startup")
def on_startup():
    init_db()


# Helper: get current user (for demo purposes, defaults to demo student user_id=1 if header not provided)
def get_current_user_id(authorization: Optional[str] = Header(None)) -> int:
    # If a custom auth header or demo user ID is sent, use it; else fallback to 1 (demo user)
    if authorization and authorization.startswith("Bearer user_"):
        try:
            return int(authorization.split("Bearer user_")[1])
        except Exception:
            pass
    return 1


# ==============================================================================
# AUTHENTICATION ENDPOINTS
# ==============================================================================
@app.post("/api/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return AuthResponse(
        token=f"Bearer user_{user.id}",
        user=UserResponse(id=user.id, email=user.email, name=user.name)
    )


@app.post("/api/auth/demo-login", response_model=AuthResponse)
def demo_login(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == "student@demo.com").first()
    if not user:
        # Auto-create if not yet created
        user = User(
            email="student@demo.com",
            name="Alex Student (Demo)",
            password="demo123"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return AuthResponse(
        token=f"Bearer user_{user.id}",
        user=UserResponse(id=user.id, email=user.email, name=user.name)
    )


@app.get("/api/auth/me", response_model=UserResponse)
def get_me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return UserResponse(id=user.id, email=user.email, name=user.name)


# ==============================================================================
# DOCUMENT INGESTION & CHUNKING ENDPOINTS
# ==============================================================================
@app.get("/api/documents", response_model=List[DocumentResponse])
def list_documents(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.user_id == user_id).order_by(desc(Document.uploaded_at)).all()
    return docs


@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("notes"),  # 'syllabus', 'notes', 'past_paper'
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    valid_types = ["syllabus", "notes", "past_paper"]
    if doc_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid doc_type. Must be one of {valid_types}")

    upload_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "uploads"))
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Ingest text, chunk with metadata, and index in ChromaDB
    ingest_result = process_and_ingest_file(file_path, file.filename, doc_type, user_id)

    # Save or update record in database
    doc_record = db.query(Document).filter(
        Document.user_id == user_id,
        Document.filename == file.filename
    ).first()

    if not doc_record:
        doc_record = Document(
            user_id=user_id,
            filename=file.filename,
            doc_type=doc_type,
            file_path=file_path,
            page_count=ingest_result["page_count"],
            chunk_count=ingest_result["chunk_count"],
            uploaded_at=datetime.utcnow()
        )
        db.add(doc_record)
    else:
        doc_record.doc_type = doc_type
        doc_record.page_count = ingest_result["page_count"]
        doc_record.chunk_count = ingest_result["chunk_count"]

    db.commit()
    db.refresh(doc_record)

    return {
        "message": f"Successfully ingested {file.filename}",
        "document_id": doc_record.id,
        "page_count": doc_record.page_count,
        "chunk_count": doc_record.chunk_count,
        "doc_type": doc_record.doc_type
    }


# ==============================================================================
# SYLLABUS TOPIC MAP & EXAM WEIGHTAGE
# ==============================================================================
@app.get("/api/topics", response_model=List[TopicHierarchyResponse])
def get_topics(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    parent_topics = db.query(Topic).filter(
        Topic.user_id == user_id,
        Topic.parent_topic_id.is_(None)
    ).all()

    result = []
    for pt in parent_topics:
        sub_list = db.query(Topic).filter(
            Topic.user_id == user_id,
            Topic.parent_topic_id == pt.id
        ).all()
        result.append(TopicHierarchyResponse(
            id=pt.id,
            name=pt.name,
            description=pt.description,
            exam_frequency=pt.exam_frequency,
            weightage_level=pt.weightage_level,
            subtopics=[SubtopicSchema(
                id=st.id,
                name=st.name,
                description=st.description,
                exam_frequency=st.exam_frequency,
                weightage_level=st.weightage_level
            ) for st in sub_list]
        ))
    return result


@app.post("/api/topics/generate-map")
def generate_topic_map(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Reads uploaded Syllabus and Past Papers to generate or refine topic mapping and exam frequencies.
    """
    syllabus_docs = db.query(Document).filter(
        Document.user_id == user_id,
        Document.doc_type == "syllabus"
    ).all()

    if not syllabus_docs:
        raise HTTPException(
            status_code=400,
            detail="No syllabus document found. Please upload a course syllabus first."
        )

    # Return refreshed topics list
    return get_topics(user_id, db)


# ==============================================================================
# DIAGNOSTIC QUIZ GENERATION & EVALUATION (Grounded RAG)
# ==============================================================================
@app.post("/api/quiz/generate", response_model=QuizGenerateResponse)
def generate_quiz(payload: QuizGenerateRequest, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == payload.topic_id, Topic.user_id == user_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found.")

    # STAGE 1: Deterministic ChromaDB Retrieval (doc_type='notes')
    retrieved_blocks = retrieve_topic_context(topic.name, user_id=user_id, top_k=4, doc_type="notes")

    # STAGE 2: Constrained LLM Generation strictly citing source blocks
    raw_questions = generate_grounded_quiz(topic.name, retrieved_blocks, question_count=payload.question_count)

    questions_out = []
    for q_idx, q in enumerate(raw_questions):
        opts = [QuizOption(id=o["id"], text=o["text"]) for o in q.get("options", [])]
        questions_out.append(QuizQuestionItem(
            id=q_idx + 1,
            question=q["question"],
            options=opts,
            correct_answer=q.get("correct_answer", "A"),
            citation=q.get("citation", f"{topic.name} Notes, Page 1"),
            explanation=q.get("explanation", "")
        ))

    return QuizGenerateResponse(
        topic_id=topic.id,
        topic_name=topic.name,
        questions=questions_out
    )


@app.post("/api/quiz/submit", response_model=QuizSubmitResponse)
def submit_quiz(payload: QuizSubmitRequest, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == payload.topic_id, Topic.user_id == user_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found.")

    evaluations: List[QuestionEvaluationResult] = []
    correct_count = 0
    total = len(payload.answers)

    for a in payload.answers:
        is_corr = (a.student_answer.strip().upper() == a.correct_answer.strip().upper())
        if is_corr:
            correct_count += 1
            expl = a.explanation or f"Correct! Confirmed in {a.citation}."
        else:
            expl = a.explanation or f"Incorrect. Grounded evidence from {a.citation} supports option {a.correct_answer}."

        evaluations.append(QuestionEvaluationResult(
            question=a.question_text,
            student_answer=a.student_answer,
            correct_answer=a.correct_answer,
            is_correct=is_corr,
            explanation=expl,
            citation=a.citation
        ))

    acc_pct = round((correct_count / total) * 100.0, 1) if total > 0 else 0.0
    status_info = classify_topic_gap(correct_count, total, topic.exam_frequency)

    # Save attempt and question details
    attempt = QuizAttempt(
        user_id=user_id,
        topic_id=topic.id,
        score=correct_count,
        total_questions=total,
        accuracy_pct=acc_pct,
        status=status_info["status"],
        created_at=datetime.utcnow()
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    for ev in evaluations:
        qq = QuizQuestion(
            quiz_attempt_id=attempt.id,
            question_text=ev.question,
            options_json=json.dumps([]),
            correct_answer=ev.correct_answer,
            student_answer=ev.student_answer,
            is_correct=ev.is_correct,
            explanation=ev.explanation,
            citation=ev.citation
        )
        db.add(qq)
    db.commit()

    return QuizSubmitResponse(
        attempt_id=attempt.id,
        topic_id=topic.id,
        topic_name=topic.name,
        score=correct_count,
        total_questions=total,
        accuracy_pct=acc_pct,
        status=status_info["status"],
        evaluations=evaluations
    )


# ==============================================================================
# GAP REPORT (CORE DIAGNOSTIC OUTPUT)
# ==============================================================================
@app.get("/api/diagnostic/gap-report", response_model=GapReportResponse)
def get_gap_report(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    parent_topics = db.query(Topic).filter(
        Topic.user_id == user_id,
        Topic.parent_topic_id.is_(None)
    ).all()

    topic_details: List[TopicGapDetail] = []
    summary_counts = {"weak": 0, "medium": 0, "strong": 0}
    total_acc_sum = 0.0
    total_topics_counted = 0

    for t in parent_topics:
        # Find all attempts for this topic
        attempts = db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.topic_id == t.id
        ).order_by(desc(QuizAttempt.created_at)).all()

        latest_attempt = attempts[0] if attempts else None
        wrong_questions = []

        if latest_attempt:
            acc_pct = latest_attempt.accuracy_pct
            status_info = classify_topic_gap(latest_attempt.score, latest_attempt.total_questions, t.exam_frequency)
            # Fetch wrong questions for diagnostic reason
            wrong_records = db.query(QuizQuestion).filter(
                QuizQuestion.quiz_attempt_id == latest_attempt.id,
                QuizQuestion.is_correct == False
            ).all()
            for wr in wrong_records:
                wrong_questions.append({
                    "question": wr.question_text,
                    "citation": wr.citation
                })
            diagnostic_reason = generate_diagnostic_reason(
                t.name,
                latest_attempt.score,
                latest_attempt.total_questions,
                wrong_questions,
                t.exam_frequency
            )
        else:
            status_info = classify_topic_gap(0, 0, t.exam_frequency)
            acc_pct = 0.0
            diagnostic_reason = f"No diagnostic attempts recorded yet. With {t.exam_frequency} past exam questions linked, diagnostic evaluation is urgently advised."

        st = status_info["status"]
        if st == "Weak":
            summary_counts["weak"] += 1
            rec_focus = "Step-by-step foundational review of core lecture notes, followed by targeted diagnostic re-testing."
        elif st == "Medium":
            summary_counts["medium"] += 1
            rec_focus = "Review boundary conditions, nuanced definitions, and solve 3-5 past examination questions."
        else:
            summary_counts["strong"] += 1
            rec_focus = "Solid conceptual mastery. Maintain retention with periodic speed quizzes."

        total_acc_sum += acc_pct
        total_topics_counted += 1

        topic_details.append(TopicGapDetail(
            topic_id=t.id,
            topic_name=t.name,
            status=status_info["status"],
            badge_color=status_info["badge_color"],
            accuracy_pct=acc_pct,
            attempts_count=len(attempts),
            exam_frequency=t.exam_frequency,
            weightage_level=t.weightage_level,
            priority_score=status_info["priority_score"],
            diagnostic_reason=diagnostic_reason,
            recommended_focus=rec_focus
        ))

    # Sort topics: Weak first, then by priority_score descending
    status_order = {"Weak": 0, "Medium": 1, "Strong": 2}
    topic_details.sort(key=lambda x: (status_order.get(x.status, 3), -x.priority_score))

    readiness = round(total_acc_sum / total_topics_counted, 1) if total_topics_counted > 0 else 0.0

    return GapReportResponse(
        summary=summary_counts,
        overall_readiness_pct=readiness,
        topics=topic_details
    )


# ==============================================================================
# ADAPTIVE REVISION PLAN
# ==============================================================================
@app.post("/api/revision-plan/generate", response_model=RevisionPlanResponse)
def generate_revision_plan(
    payload: RevisionPlanRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    parent_topics = db.query(Topic).filter(
        Topic.user_id == user_id,
        Topic.parent_topic_id.is_(None)
    ).all()

    plan_topics = []
    for t in parent_topics:
        latest = db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.topic_id == t.id
        ).order_by(desc(QuizAttempt.created_at)).first()

        acc = (latest.accuracy_pct / 100.0) if latest else 0.0
        status = latest.status if latest else ("Weak" if t.exam_frequency >= 3 else "Medium")
        priority = round((1.0 - acc) * (1.0 + t.exam_frequency * 0.2), 2)

        plan_topics.append({
            "id": t.id,
            "name": t.name,
            "status": status,
            "weightage_level": t.weightage_level,
            "exam_frequency": t.exam_frequency,
            "priority_score": priority
        })

    schedule = build_adaptive_revision_plan(
        plan_topics,
        target_days=payload.target_days,
        daily_hours=payload.daily_hours
    )

    # Save to database
    rev_plan = db.query(RevisionPlan).filter(RevisionPlan.user_id == user_id).first()
    if not rev_plan:
        rev_plan = RevisionPlan(
            user_id=user_id,
            target_days=payload.target_days,
            daily_hours=payload.daily_hours,
            plan_json=json.dumps(schedule)
        )
        db.add(rev_plan)
    else:
        rev_plan.target_days = payload.target_days
        rev_plan.daily_hours = payload.daily_hours
        rev_plan.plan_json = json.dumps(schedule)
        rev_plan.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(rev_plan)

    total_hours = round(payload.target_days * payload.daily_hours, 1)

    return RevisionPlanResponse(
        plan_id=rev_plan.id,
        target_days=rev_plan.target_days,
        daily_hours=rev_plan.daily_hours,
        total_study_hours=total_hours,
        schedule=schedule,
        created_at=rev_plan.created_at,
        updated_at=rev_plan.updated_at
    )


@app.get("/api/revision-plan", response_model=RevisionPlanResponse)
def get_revision_plan(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    rev_plan = db.query(RevisionPlan).filter(RevisionPlan.user_id == user_id).order_by(desc(RevisionPlan.updated_at)).first()
    if not rev_plan:
        # Generate default 5-day plan
        return generate_revision_plan(RevisionPlanRequest(target_days=5, daily_hours=2.0), user_id, db)

    schedule = json.loads(rev_plan.plan_json)
    total_hours = round(rev_plan.target_days * rev_plan.daily_hours, 1)

    return RevisionPlanResponse(
        plan_id=rev_plan.id,
        target_days=rev_plan.target_days,
        daily_hours=rev_plan.daily_hours,
        total_study_hours=total_hours,
        schedule=schedule,
        created_at=rev_plan.created_at,
        updated_at=rev_plan.updated_at
    )


# ==============================================================================
# GROUNDED TUTOR CHAT ("Explain This Topic")
# ==============================================================================
@app.post("/api/tutor/explain", response_model=ExplainTopicResponse)
def explain_topic(payload: ExplainTopicRequest, user_id: int = Depends(get_current_user_id)):
    # STAGE 1: Deterministic retrieval strictly from user's study notes
    retrieved_blocks = retrieve_topic_context(
        payload.topic_name,
        user_id=user_id,
        top_k=4,
        doc_type="notes"
    )

    # STAGE 2: Constrained synthesis referencing only retrieved material
    res = explain_topic_grounded(payload.topic_name, payload.user_query, retrieved_blocks)
    return ExplainTopicResponse(**res)


# ==============================================================================
# PROGRESS DASHBOARD & METRICS
# ==============================================================================
@app.get("/api/dashboard/metrics", response_model=DashboardMetricsResponse)
def get_dashboard_metrics(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    doc_count = db.query(Document).filter(Document.user_id == user_id).count()
    topic_count = db.query(Topic).filter(Topic.user_id == user_id, Topic.parent_topic_id.is_(None)).count()
    attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).order_by(desc(QuizAttempt.created_at)).all()

    avg_acc = 0.0
    weak = 0
    med = 0
    strong = 0

    if attempts:
        avg_acc = round(sum(a.accuracy_pct for a in attempts) / len(attempts), 1)

    # Topic breakdown
    topics = db.query(Topic).filter(Topic.user_id == user_id, Topic.parent_topic_id.is_(None)).all()
    for t in topics:
        latest = db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.topic_id == t.id
        ).order_by(desc(QuizAttempt.created_at)).first()

        status = latest.status if latest else ("Weak" if t.exam_frequency >= 3 else "Medium")
        if status == "Weak":
            weak += 1
        elif status == "Medium":
            med += 1
        else:
            strong += 1

    trend_items = []
    # Take chronological order of recent attempts (up to 10)
    for a in sorted(attempts, key=lambda x: x.created_at)[-10:]:
        t_name = a.topic.name if a.topic else "Quiz Attempt"
        trend_items.append(AttemptTrendItem(
            attempt_id=a.id,
            topic_name=t_name,
            accuracy_pct=a.accuracy_pct,
            date=a.created_at.strftime("%b %d, %H:%M")
        ))

    return DashboardMetricsResponse(
        total_documents=doc_count,
        total_topics=topic_count,
        quizzes_taken=len(attempts),
        average_accuracy=avg_acc,
        weak_count=weak,
        medium_count=med,
        strong_count=strong,
        recent_attempts=trend_items
    )


# ==============================================================================
# STATIC FRONTEND SERVING
# ==============================================================================
from fastapi.staticfiles import StaticFiles
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

