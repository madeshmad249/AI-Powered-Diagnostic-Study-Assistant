import pytest
from fastapi.testclient import TestClient
from main import app
from diagnostic import classify_topic_gap, build_adaptive_revision_plan
from rag_engine import retrieve_topic_context

client = TestClient(app)


def test_auth_demo_login():
    response = client.post("/api/auth/demo-login")
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["email"] == "student@demo.com"
    assert data["user"]["name"] == "Alex Student (Demo)"


def test_documents_list():
    response = client.get("/api/documents")
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) >= 5
    filenames = [d["filename"] for d in docs]
    assert "OS_Course_Syllabus.txt" in filenames
    assert "OS_Chapter1_Processes_and_Threads.txt" in filenames
    assert any(d["chunk_count"] > 0 for d in docs)


def test_topics_hierarchy():
    response = client.get("/api/topics")
    assert response.status_code == 200
    topics = response.json()
    assert len(topics) >= 4
    topic_names = [t["name"] for t in topics]
    assert "Memory Management & Virtual Memory" in topic_names
    # Check subtopics and exam frequency
    mem_topic = next(t for t in topics if "Memory" in t["name"])
    assert len(mem_topic["subtopics"]) >= 3
    assert mem_topic["exam_frequency"] >= 3


def test_deterministic_retrieval():
    # Stage 1 Retrieval: user_id=1, doc_type='notes'
    blocks = retrieve_topic_context("Paging and Virtual Memory", user_id=1, top_k=3, doc_type="notes")
    assert len(blocks) > 0
    for b in blocks:
        assert "citation" in b
        assert "Page" in b["citation"]
        assert "content" in b
        assert len(b["content"]) > 20


def test_grounded_quiz_generation():
    topics_res = client.get("/api/topics")
    mem_topic = topics_res.json()[0]

    payload = {"topic_id": mem_topic["id"], "question_count": 2}
    response = client.post("/api/quiz/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == mem_topic["id"]
    assert len(data["questions"]) == 2
    for q in data["questions"]:
        assert len(q["options"]) == 4
        assert q["citation"] != ""
        assert "Page" in q["citation"]


def test_quiz_submission_and_evaluation():
    topics_res = client.get("/api/topics")
    topic = topics_res.json()[0]

    submission = {
        "topic_id": topic["id"],
        "answers": [
            {
                "question_index": 1,
                "question_text": "What does TLB stand for and do?",
                "options": [
                    {"id": "A", "text": "Translation Lookaside Buffer"},
                    {"id": "B", "text": "Total Limit Block"}
                ],
                "student_answer": "A",
                "correct_answer": "A",
                "citation": "OS_Chapter2_Memory_Management_and_Paging.txt, Page 2",
                "explanation": "Page 2 confirms TLB caches page-table entries."
            },
            {
                "question_index": 2,
                "question_text": "What triggers a page fault?",
                "options": [
                    {"id": "A", "text": "Clock interrupt"},
                    {"id": "B", "text": "Invalid page bit reference"}
                ],
                "student_answer": "A",
                "correct_answer": "B",
                "citation": "OS_Chapter2_Memory_Management_and_Paging.txt, Page 3",
                "explanation": "Page 3 indicates an invalid bit triggers a trap to kernel."
            }
        ]
    }

    response = client.post("/api/quiz/submit", json=submission)
    assert response.status_code == 200
    result = response.json()
    assert result["score"] == 1
    assert result["total_questions"] == 2
    assert result["accuracy_pct"] == 50.0
    assert result["status"] in ["Weak", "Medium", "Strong"]
    assert len(result["evaluations"]) == 2
    assert result["evaluations"][0]["is_correct"] is True
    assert result["evaluations"][1]["is_correct"] is False


def test_gap_classification_formula():
    weak = classify_topic_gap(1, 3, 5)
    assert weak["status"] == "Weak"
    assert weak["badge_color"] == "red"
    assert weak["priority_score"] > 1.0

    med = classify_topic_gap(2, 3, 2)
    assert med["status"] == "Medium"
    assert med["badge_color"] == "yellow"

    strong = classify_topic_gap(3, 3, 1)
    assert strong["status"] == "Strong"
    assert strong["badge_color"] == "green"
    assert strong["priority_score"] == 0.0


def test_gap_report_endpoint():
    response = client.get("/api/diagnostic/gap-report")
    assert response.status_code == 200
    report = response.json()
    assert "summary" in report
    assert "topics" in report
    assert len(report["topics"]) >= 4

    # Check that diagnostic reasons exist and cite evidence
    first_topic = report["topics"][0]
    assert first_topic["diagnostic_reason"] != ""
    assert "priority_score" in first_topic


def test_adaptive_revision_plan():
    payload = {"target_days": 4, "daily_hours": 2.5}
    response = client.post("/api/revision-plan/generate", json=payload)
    assert response.status_code == 200
    plan = response.json()
    assert plan["target_days"] == 4
    assert len(plan["schedule"]) == 4
    for day in plan["schedule"]:
        assert len(day["blocks"]) > 0
        assert day["total_study_minutes"] > 0


def test_grounded_tutor_explain():
    payload = {
        "topic_name": "Memory Management & Virtual Memory",
        "user_query": "Explain what a page fault is and how it is handled."
    }
    response = client.post("/api/tutor/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["grounded_in_material"] is True
    assert len(data["explanation"]) > 30
    assert len(data["citations"]) > 0


def test_dashboard_metrics():
    response = client.get("/api/dashboard/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] >= 5
    assert data["total_topics"] >= 4
    assert data["quizzes_taken"] >= 3
    assert len(data["recent_attempts"]) >= 3
