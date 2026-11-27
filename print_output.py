import urllib.request
import json

BASE = "http://127.0.0.1:8000"

def get(path, token=None):
    headers = {"Authorization": token} if token else {}
    req = urllib.request.Request(f"{BASE}{path}", headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def post(path, data, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = token
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

print("=" * 75)
print("GAPFINDER AI: LIVE SYSTEM EXECUTION OUTPUT")
print("=" * 75)

# 1. Login
auth = post("/api/auth/demo-login", {})
token = auth["token"]
user = auth["user"]
print(f"\n[1] AUTHENTICATION & DEMO LOGIN:")
print(f"    Student: {user['name']} ({user['email']})")
print(f"    Session Token: {token}")

# 2. Documents
docs = get("/api/documents", token)
print(f"\n[2] DOCUMENT INGESTION & CHROMADB VECTOR STORE:")
for d in docs:
    print(f"    * {d['filename']:<46} | Type: {d['doc_type']:<10} | Pages: {d['page_count']} | ChromaDB Chunks: {d['chunk_count']}")

# 3. Topic Map
topics = get("/api/topics", token)
print(f"\n[3] SYLLABUS TOPIC MAP & EXAM WEIGHTAGE:")
for idx, t in enumerate(topics, 1):
    print(f"    {idx}. {t['name']}")
    print(f"       Weightage: {t['weightage_level']} ({t['exam_frequency']} Past Exam Questions linked)")
    sub_names = ", ".join([s["name"] for s in t["subtopics"][:3]])
    print(f"       Key Subtopics: {sub_names}")

# 4. Grounded Quiz Generation
quiz = post("/api/quiz/generate", {"topic_id": topics[0]["id"], "question_count": 2}, token)
print(f"\n[4] GROUNDED DIAGNOSTIC QUIZ GENERATION (WITH CITATIONS):")
print(f"    Topic: {quiz['topic_name']}")
for q_idx, q in enumerate(quiz["questions"], 1):
    print(f"    Q{q_idx}: {q['question']}")
    print(f"        -> Grounded Citation Badge: [{q['citation']}]")
    for opt in q["options"]:
        print(f"           [{opt['id']}] {opt['text']}")

# 5. Gap Report
gap = get("/api/diagnostic/gap-report", token)
print(f"\n[5] GAP REPORT (CORE STUDY DOCTOR OUTPUT):")
print(f"    Overall Readiness: {gap['overall_readiness_pct']}% | Breakdown: {gap['summary']}")
for td in gap["topics"]:
    print(f"\n    * [{td['status'].upper()} TIER] {td['topic_name']}")
    print(f"      Accuracy: {td['accuracy_pct']}% | Priority Score: {td['priority_score']} (Weight: {td['weightage_level']})")
    print(f"      Diagnosis: {td['diagnostic_reason']}")
    print(f"      Prescription: {td['recommended_focus']}")

# 6. Revision Plan
plan = get("/api/revision-plan", token)
print(f"\n[6] ADAPTIVE REVISION PLAN ({plan['target_days']} Days, {plan['daily_hours']} Hrs/Day):")
for day in plan["schedule"][:3]:
    print(f"\n    {day['day_title']} ({day['total_study_minutes']} mins):")
    for b in day["blocks"]:
        print(f"      * [{b['time_allocated_minutes']} mins] {b['topic_name']} ({b['status']})")
        print(f"        Objective: {b['focus_objective']}")

# 7. Grounded Tutor
tutor = post("/api/tutor/explain", {
    "topic_name": "Memory Management & Virtual Memory",
    "user_query": "What triggers a page fault and how does demand paging handle it?"
}, token)
print(f"\n[7] GROUNDED 'EXPLAIN THIS TOPIC' TUTOR (ZERO HALLUCINATION):")
print(f"    Topic: {tutor['topic_name']}")
print(f"    Verified Grounded Citations: {len(tutor['citations'])} excerpts found")
for c in tutor["citations"][:2]:
    print(f"      [Source: {c['filename']}, Page {c['page']}]")
print(f"    Explanation Excerpt:\n    {tutor['explanation'][:280]}...")

print("\n" + "=" * 75)
print("LIVE WEB UI IS ACTIVE AT: http://127.0.0.1:8000")
print("=" * 75)
