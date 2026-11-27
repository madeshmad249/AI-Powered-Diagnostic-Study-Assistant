# GapFinder AI — AI-Powered Diagnostic Study Assistant

> **Assignment Reference**: Full-stack, AI-powered diagnostic study application that acts as a "Study Doctor." It ingests a student's course materials, tests their understanding using grounded questions, diagnoses exact knowledge gaps, and generates an adaptive, time-bound revision plan.

---

## 🌟 Key Features & Architecture

### 1. User Authentication & Persistence (Step 1)
- Demo account pre-seeded: **`student@demo.com` / `demo123`** with 1-click instant login.
- Relational SQLite database tracking user profiles, uploaded documents, topic trees, quiz attempts, question breakdown, and adaptive revision schedules.

### 2. Document Ingestion & Chunking Pipeline (Step 2)
- Upload support for **PDFs**, **text**, and **markdown** files categorized into:
  - **Syllabus**: Used to extract course modules and topic hierarchy.
  - **Study Notes & Textbooks**: Ingested and chunked (~600 chars with 100 char overlap) with attached metadata (`filename`, `doc_type`, `page`).
  - **Past Exam Papers**: Extracted exam questions linked to topics to calculate topic exam frequency.
- Indexed into a persistent local **ChromaDB** vector store.

### 3. Syllabus Topic Map & Exam Weightage (Step 3)
- Hierarchical syllabus tree structure (Modules -> Topics -> Subtopics).
- Exam weightage badges (High, Medium, Low) based on vector-matched past paper frequency.

### 4. Strict Two-Stage RAG Architecture (Step 4)
- **Stage A — Retrieval Only (Deterministic Search)**:
  Queries ChromaDB filtered strictly by `user_id` and `doc_type="notes"`. Fetches top 3–5 excerpts with metadata (`[Source: filename, Page X]`). No LLM generation occurs in this stage.
- **Stage B — Generation (Constrained Synthesis)**:
  Passes strictly the retrieved excerpts into Gemini LLM (with offline grounded fallback). Instructs the model: *"Use ONLY the provided context. Cite the exact filename and page_number."*

### 5. Grounded Diagnostic Quiz & Answer Evaluator (Step 5)
- Generates 3-question diagnostic quizzes grounded in the student's notes with source badges (e.g. `OS_Chapter2_Memory_Management_and_Paging.txt, Page 2`).
- Real-time answer evaluation comparing student choices against source excerpts with educational explanations.

### 6. Gap Report — The Core Diagnosis (Step 6)
- Categorizes topics into medical diagnostic tiers:
  - 🔴 **Weak Tier (< 50% accuracy or unattempted high-yield topics)**: Critical deficits.
  - 🟡 **Medium Tier (50% – 79% accuracy)**: Nuanced boundary edge cases.
  - 🟢 **Strong Tier (≥ 80% accuracy)**: Conceptual mastery.
- Generates specific clinical diagnostic reasons:
  > *"Critical gap: Missed 2 of 3 questions (33.3% accuracy), struggling particularly with: 'During demand paging, what exact hardware event initiates the operating system page fault handler?' (OS_Chapter2_Memory_Management_and_Paging.txt, Page 3)."*

### 7. Adaptive Revision Plan & Grounded Tutor (Step 7)
- Dynamic timetable customized to student's constraints (**Days Remaining** and **Daily Available Hours**).
- Prioritized via the formula:
  $$\text{Priority} = (1 - \text{Accuracy}) \times (1 + \text{Exam\_Frequency} \times 0.2)$$
- Automatically recalculates and promotes/demotes topics when quizzes are retaken.
- Grounded "Explain this topic" assistant strictly answering from course notes with verified citation tags.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Node.js 18+ (tested on v25.9)

### 1. Run the Full Application (Single Command)
```bash
cd C:\Users\mades\.gemini\antigravity\scratch\diagnostic-study-ai
python run.py
```
Open your browser at: **`http://127.0.0.1:8000`**

### 2. Evaluator Credentials
- **Email**: `student@demo.com`
- **Password**: `demo123`
*(Or click the **"Log In with Demo Account (1-Click)"** button on the login screen)*

---

## 🧪 Running Automated Tests

A comprehensive pytest test suite verifies the entire system:
```bash
cd backend
pytest test_diagnostic.py -v
```
**Test Coverage**:
- `test_auth_demo_login`: Verifies authentication and session token.
- `test_documents_list`: Verifies document ingestion and ChromaDB chunk count.
- `test_topics_hierarchy`: Verifies syllabus tree and exam weightage calculation.
- `test_deterministic_retrieval`: Verifies Stage 1 ChromaDB retrieval filtered strictly by notes with page numbers.
- `test_grounded_quiz_generation`: Verifies Stage 2 question synthesis with citations.
- `test_quiz_submission_and_evaluation`: Verifies scoring, grading, and explanation generation.
- `test_gap_classification_formula`: Verifies Weak (<50%), Medium (50-79%), Strong (>=80%) thresholds.
- `test_gap_report_endpoint`: Verifies qualitative diagnostic gap reasoning.
- `test_adaptive_revision_plan`: Verifies time-bound priority scheduling.
- `test_grounded_tutor_explain`: Verifies grounded Q&A with citations.
- `test_dashboard_metrics`: Verifies attempt-over-attempt trend metrics.

---

## 📂 Project Directory Structure

```
diagnostic-study-ai/
├── backend/
│   ├── main.py                  # FastAPI server with all REST endpoints & static mounting
│   ├── database.py              # SQLite models (User, Document, Topic, QuizAttempt, RevisionPlan)
│   ├── models.py                # Pydantic schemas for structured JSON validation
│   ├── ingestion.py             # PDF text extraction, chunking, and ChromaDB indexing
│   ├── rag_engine.py            # Strict Stage 1 Retrieval vs Stage 2 Grounded Generation
│   ├── diagnostic.py            # Gap diagnosis, clinical reasons, and adaptive plan builder
│   ├── seed_demo.py             # Demo account & CS301 OS course materials seeder
│   └── test_diagnostic.py       # 11 comprehensive automated tests
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx        # Demo login with 1-click access
│   │   │   ├── Upload.jsx       # Syllabus, notes, and past paper uploader & chunk tracker
│   │   │   ├── TopicMap.jsx     # Syllabus hierarchy with past paper weightages
│   │   │   ├── Quiz.jsx         # Diagnostic quiz with source citation badges & grading
│   │   │   ├── GapReport.jsx    # Core output: Weak/Med/Strong diagnosis with clinical reasons
│   │   │   ├── RevisionPlan.jsx # Dynamic timetable by priority formula & time constraints
│   │   │   └── Dashboard.jsx    # Attempt-over-attempt score trend charts & KPIs
│   │   ├── components/
│   │   │   ├── Navbar.jsx       # Header with Study Doctor brand & view switcher
│   │   │   └── TopicChat.jsx    # Grounded "Explain this topic" tutor with citation tags
│   │   ├── api.js               # Centralized REST API client
│   │   ├── App.jsx              # App layout, state synchronization, and view router
│   │   └── index.css            # Tailwind CSS styling & animations
│   ├── dist/                    # Compiled production build served by FastAPI
│   └── vite.config.js           # Vite config with Tailwind & backend proxy
├── storage/
│   ├── uploads/                 # Stored raw course documents (.txt, .pdf)
│   ├── chroma_db/               # Persistent local ChromaDB vector database
│   └── study_app.db             # SQLite relational database
├── run.py                       # Single command application launcher
└── README.md                    # Project documentation
```
