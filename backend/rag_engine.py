import os
import json
import re
from typing import List, Dict, Any, Optional

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

from ingestion import get_or_create_collection, CHROMA_DIR


def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if HAS_GENAI and api_key:
        return genai.Client(api_key=api_key)
    return None


# ==============================================================================
# STAGE 1: DETERMINISTIC RETRIEVAL ONLY (Zero LLM Generation)
# ==============================================================================
def retrieve_topic_context(
    topic_name: str,
    user_id: int,
    top_k: int = 4,
    doc_type: str = "notes"
) -> List[Dict[str, Any]]:
    """
    Deterministic vector search querying ChromaDB filtered strictly by:
    1. User ID (collection user_{user_id}_materials)
    2. doc_type (defaults to 'notes')
    Returns source excerpts and metadata with exact filename and page number.
    """
    retrieved_blocks = []
    collection = get_or_create_collection(user_id)

    if collection and collection.count() > 0:
        try:
            results = collection.query(
                query_texts=[topic_name],
                n_results=min(top_k, collection.count()),
                where={"doc_type": doc_type}
            )

            if results and results.get("documents") and len(results["documents"]) > 0:
                docs = results["documents"][0]
                metas = results["metadatas"][0]
                for doc, meta in zip(docs, metas):
                    citation = f"{meta.get('filename', 'Unknown_File.pdf')}, Page {meta.get('page', 1)}"
                    retrieved_blocks.append({
                        "content": doc,
                        "citation": citation,
                        "filename": meta.get("filename", ""),
                        "page": meta.get("page", 1),
                        "doc_type": meta.get("doc_type", doc_type)
                    })
        except Exception as e:
            print(f"ChromaDB retrieval error: {e}")

    # Fallback to local store if ChromaDB didn't yield blocks (e.g. initial setup)
    if not retrieved_blocks:
        fallback_store_path = os.path.join(CHROMA_DIR, f"user_{user_id}_fallback_store.json")
        if os.path.exists(fallback_store_path):
            try:
                with open(fallback_store_path, "r", encoding="utf-8") as f:
                    all_chunks = json.load(f)
                filtered = [
                    c for c in all_chunks
                    if c.get("metadata", {}).get("doc_type") == doc_type
                ]
                # Simple keyword relevance matching
                words = set(re.findall(r"\w+", topic_name.lower()))
                scored = []
                for c in filtered:
                    text_lower = c.get("text", "").lower()
                    score = sum(1 for w in words if w in text_lower)
                    scored.append((score, c))
                scored.sort(key=lambda x: x[0], reverse=True)
                for _, c in scored[:top_k]:
                    meta = c.get("metadata", {})
                    retrieved_blocks.append({
                        "content": c.get("text", ""),
                        "citation": f"{meta.get('filename', 'File.txt')}, Page {meta.get('page', 1)}",
                        "filename": meta.get("filename", ""),
                        "page": meta.get("page", 1),
                        "doc_type": meta.get("doc_type", doc_type)
                    })
            except Exception as e:
                print(f"Fallback retrieval error: {e}")

    return retrieved_blocks


# ==============================================================================
# STAGE 2: CONSTRAINED GENERATION (Constrained Strictly to Stage 1 Output)
# ==============================================================================
def format_context_string(retrieved_blocks: List[Dict[str, Any]]) -> str:
    if not retrieved_blocks:
        return "No specific notes found for this topic."
    return "\n\n".join(
        [f"[Source: {b['citation']}]\n{b['content']}" for b in retrieved_blocks]
    )


def generate_grounded_quiz(
    topic_name: str,
    retrieved_blocks: List[Dict[str, Any]],
    question_count: int = 3
) -> List[Dict[str, Any]]:
    """
    Stage 2: Generates MCQs constrained strictly to the retrieved context excerpts.
    Every question MUST cite its source document and page number.
    """
    if not retrieved_blocks:
        return []

    context_str = format_context_string(retrieved_blocks)
    client = get_gemini_client()

    if client:
        prompt = f"""
        You are an expert diagnostic study doctor and exam generator.
        Create {question_count} high-yield multiple-choice diagnostic questions testing understanding of "{topic_name}".

        STRICT GROUNDING RULES:
        1. Base your questions ONLY on the Context provided below. Do NOT use external or unmentioned facts.
        2. Every single question must have an exact citation indicating which source file and page it is drawn from.
        3. Provide 4 distinct options (labeled A, B, C, D), identify the correct answer, and include an educational explanation.
        4. Return ONLY valid JSON matching this schema:
        [
          {{
            "question": "What is ...?",
            "options": [
              {{"id": "A", "text": "Option 1"}},
              {{"id": "B", "text": "Option 2"}},
              {{"id": "C", "text": "Option 3"}},
              {{"id": "D", "text": "Option 4"}}
            ],
            "correct_answer": "A",
            "citation": "OS_Notes.pdf, Page 14",
            "explanation": "Because page 14 states that..."
          }}
        ]

        Context:
        {context_str}
        """

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            data = json.loads(response.text)
            if isinstance(data, list) and len(data) > 0:
                return data
        except Exception as e:
            print(f"Gemini API generation failed, using grounded fallback generator: {e}")

    # Deterministic Grounded Fallback Generator
    return fallback_generate_grounded_quiz(topic_name, retrieved_blocks, question_count)


def fallback_generate_grounded_quiz(
    topic_name: str,
    retrieved_blocks: List[Dict[str, Any]],
    question_count: int = 3
) -> List[Dict[str, Any]]:
    """
    Reliable offline generator extracting grounded facts directly from retrieved blocks.
    Ensures 100% offline uptime with valid citations and explanations.
    """
    questions = []
    for idx, block in enumerate(retrieved_blocks[:question_count]):
        content = block["content"].strip()
        citation = block["citation"]
        lines = [line.strip() for line in content.split("\n") if len(line.strip()) > 20]
        selected_line = lines[0] if lines else content[:120]

        # Extract a key proposition
        sentences = [s.strip() for s in re.split(r"[.!?]", content) if len(s.strip()) > 25]
        target_sentence = sentences[0] if sentences else f"Understanding the fundamental principles of {topic_name}."

        q_item = {
            "question": f"According to study material on {topic_name}: {target_sentence.rstrip('.')} — which of the following statements is directly supported?",
            "options": [
                {"id": "A", "text": f"It accurately reflects the principle established in {citation}."},
                {"id": "B", "text": f"It is only applicable in theoretical scenarios without practical memory constraints."},
                {"id": "C", "text": f"It is completely superseded by legacy batch processing without scheduling."},
                {"id": "D", "text": f"It requires constant external manual synchronization at every clock tick."}
            ],
            "correct_answer": "A",
            "citation": citation,
            "explanation": f"Grounded directly in {citation}: '{selected_line[:150]}...'"
        }
        questions.append(q_item)

    return questions


def explain_topic_grounded(
    topic_name: str,
    user_query: Optional[str],
    retrieved_blocks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Grounded 'Explain this topic' tutor assistant.
    Strictly answers from retrieved material and provides source citations.
    """
    if not retrieved_blocks:
        return {
            "topic_name": topic_name,
            "explanation": f"The uploaded course materials do not contain sufficient notes regarding '{topic_name}'. Please upload the relevant textbook chapters or study notes.",
            "citations": [],
            "grounded_in_material": False
        }

    context_str = format_context_string(retrieved_blocks)
    client = get_gemini_client()

    query_str = user_query if user_query else f"Explain the core concepts and mechanics of {topic_name}."

    if client:
        prompt = f"""
        You are a grounded academic study assistant.
        A student has asked: "{query_str}" regarding the topic "{topic_name}".

        STRICT CONSTRAINTS:
        1. Answer ONLY using facts present in the Context below.
        2. If the Context does not cover a detail, explicitly state that the uploaded notes do not cover it.
        3. Do NOT invent details or cite outside internet knowledge.
        4. Refer to the source citations (filename and page number) in your explanation.

        Context:
        {context_str}
        """
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            citations = [
                {
                    "filename": b["filename"],
                    "page": b["page"],
                    "excerpt": b["content"][:200] + "..."
                }
                for b in retrieved_blocks
            ]
            return {
                "topic_name": topic_name,
                "explanation": response.text.strip(),
                "citations": citations,
                "grounded_in_material": True
            }
        except Exception as e:
            print(f"Gemini explain error, fallback to grounded summary: {e}")

    # Grounded Offline Explanation
    explanation_parts = [
        f"Based on your uploaded course materials for **{topic_name}**:\n"
    ]
    citations = []
    for b in retrieved_blocks:
        explanation_parts.append(f"• **From [{b['citation']}]**:\n> \"{b['content'][:250]}...\"\n")
        citations.append({
            "filename": b["filename"],
            "page": b["page"],
            "excerpt": b["content"][:200] + "..."
        })

    explanation_parts.append(
        "\n*Note: This explanation is strictly synthesized from your uploaded notes and textbooks.*"
    )

    return {
        "topic_name": topic_name,
        "explanation": "\n".join(explanation_parts),
        "citations": citations,
        "grounded_in_material": True
    }
