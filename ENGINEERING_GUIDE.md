# Comprehensive Engineering Guide: AI-Powered Diagnostic Study Assistant (GapFinder AI)

## 1. Executive Summary & Problem Breakdown

### What is the Platform?

**GapFinder AI** acts as an automated "Study Doctor" for academic students. Unlike standard conversational chatbots that passively wait for students to ask questions (which fails because students cannot ask about knowledge deficits they are unaware of), GapFinder AI proactively:
1. Ingests full course materials (Syllabus, Textbook Notes, Past Exam Papers).
2. Maps topics, subtopics, and exam weightages.
3. Tests student comprehension through grounded diagnostic questions with exact source citations.
4. Evaluates submissions and generates a medical-style **Gap Report** sorting topics into **Weak**, **Medium**, and **Strong** tiers with qualitative diagnoses.
5. Produces a prioritized, time-bound **Adaptive Revision Plan** that updates dynamically upon quiz retakes.

```
+-----------------------------------------------------------------------------------+
| 1. DOCUMENT INGESTION & TOPIC MAPPING                                             |
|    Uploads: Syllabus, Notes, Past Exam Papers -> Page-by-page Vector Chunks       |
|    Matches past exam questions to topics -> Calculates exam frequency             |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 2. STRICT TWO-STAGE RAG (RETRIEVAL-AUGMENTED GENERATION)                          |
|    Stage A: Deterministic Vector Search (ChromaDB, notes only, top_k=4)           |
|    Stage B: Constrained LLM Synthesis (Zero external knowledge, exact page cite)  |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 3. GROUNDED DIAGNOSTIC QUIZ & ANSWER EVALUATION                                   |
|    Tests conceptual understanding with source citations (e.g., "Page 14")         |
|    Evaluates right/wrong answers with grounded educational explanations           |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 4. GAP REPORT (THE CORE DIAGNOSTIC OUTPUT)                                        |
|    🔴 Weak (<50%): Urgent Knowledge Deficit                                       |
|    🟡 Medium (50-79%): Nuanced Boundary Confusion                                 |
|    🟢 Strong (>=80%): Conceptual Mastery                                          |
|    Synthesizes clinical diagnostic reason explaining exactly why concepts failed  |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 5. ADAPTIVE TIME-BOUND REVISION PLAN & GROUNDED TUTOR                             |
|    Priority Formula: Priority = (1 - Accuracy) * (1 + Exam_Weight * 0.2)          |
|    Allocates daily hours across target exam days; updates after retakes           |
+-----------------------------------------------------------------------------------+
```

---

## 2. End-to-End System Architecture

```mermaid
flowchart TD
    subgraph Client ["Frontend Layer (React + Tailwind CSS)"]
        UI_Login[Login.jsx (1-Click Demo)]
        UI_Upload[Upload.jsx (Ingestion & Chunk Tracker)]
        UI_TopicMap[TopicMap.jsx (Syllabus & Weightage)]
        UI_Quiz[Quiz.jsx (Grounded Testing & Feedback)]
        UI_Gap[GapReport.jsx (Weak/Med/Strong Diagnosis)]
        UI_Plan[RevisionPlan.jsx (Adaptive Schedule)]
        UI_Dash[Dashboard.jsx (Attempt Trends & KPIs)]
        UI_Chat[TopicChat.jsx (Grounded Tutor Sidebar)]
    end

    subgraph API ["REST API Layer (FastAPI)"]
        Router_Auth[/api/auth]
        Router_Docs[/api/documents]
        Router_Topics[/api/topics]
        Router_Quiz[/api/quiz]
        Router_Diag[/api/diagnostic/gap-report]
        Router_Plan[/api/revision-plan]
        Router_Tutor[/api/tutor/explain]
        Router_Dash[/api/dashboard/metrics]
    end

    subgraph CoreEngine ["Core Engine & Separation of Concerns"]
        Ingest[ingestion.py: Page-aware chunking & metadata]
        RAG[rag_engine.py: Strict Stage 1 Retrieval vs Stage 2 Generation]
        Diag[diagnostic.py: Gap Classifier & Priority Scheduler]
    end

    subgraph StorageLayer ["Persistence & Vector Store"]
        SQLite[(study_app.db: SQLite / SQLAlchemy)]
        Chroma[(chroma_db: ChromaDB Vector Store)]
        Files[(uploads: Raw PDFs & Text Files)]
    end

    Client --> API
    API --> CoreEngine
    CoreEngine --> StorageLayer
```

---

## 3. Strict Two-Stage RAG Specification

To guarantee that the AI never hallucinates or leaks ungrounded outside knowledge:

1. **Stage 1 — Deterministic Retrieval (No LLM):**
   ```python
   def retrieve_topic_context(topic_name: str, user_id: int, top_k: int = 4, doc_type: str = "notes"):
       # Queries ChromaDB collection user_{user_id}_materials
       # Strictly filters where={"doc_type": "notes"}
       # Returns top_k source excerpts with exact filename and page number
   ```
2. **Stage 2 — Constrained Generation:**
   ```python
   # Prompt enforces strict constraints:
   # 1. Use ONLY the provided Context excerpts.
   # 2. If facts are not in Context, state that the material does not cover it.
   # 3. Always output exact source citations (e.g. "OS_Notes.pdf, Page 14").
   ```

---

## 4. Priority Scoring & Adaptive Scheduling Algorithm

The revision plan prioritizes weak, high-yield exam topics using the mathematical formula:

$$\text{Priority Score} = (1.0 - \text{Accuracy}) \times (1.0 + \text{Exam\_Frequency} \times 0.2)$$

- **Knowledge Deficit Factor:** $(1.0 - \text{Accuracy})$ ensures that lower scores produce higher urgency.
- **Exam Weightage Multiplier:** $(1.0 + \text{Exam\_Frequency} \times 0.2)$ scales urgency based on the count of past exam questions linked to that topic.
- **Dynamic Adaptability:** When a student retakes a quiz and improves accuracy from 33% to 100%, the priority score drops to 0.0, automatically shrinking or removing it from future revision days.

---

## 5. Verification & Test Suite

The project includes 11 automated pytest tests in `backend/test_diagnostic.py`:
- Auth demo login verification
- Multi-format ingestion and ChromaDB chunking
- Syllabus hierarchy and past-paper weightage mapping
- Stage 1 deterministic vector retrieval
- Grounded quiz generation with citations
- Answer evaluation and scoring
- Gap classification formula (Weak <50%, Medium 50–79%, Strong ≥80%)
- Qualitative diagnostic reason synthesis
- Adaptive revision plan scheduling
- Grounded tutor Q&A
- Attempt-over-attempt score trend tracking

Execute tests:
```bash
cd backend
pytest test_diagnostic.py -v
```

---

## 6. How to Run the Full Application

```bash
python run.py
```
- Web Application: **`http://127.0.0.1:8000`**
- Interactive API Docs: **`http://127.0.0.1:8000/docs`**
- Demo Login: **`student@demo.com`** / **`demo123`** (or 1-click on the UI)
