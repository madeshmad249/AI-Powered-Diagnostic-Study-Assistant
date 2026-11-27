import os
from typing import List, Dict, Any
import pypdf

# Try to import chromadb
try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False

CHROMA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "chroma_db"))
os.makedirs(CHROMA_DIR, exist_ok=True)


def get_chroma_client():
    if HAS_CHROMADB:
        return chromadb.PersistentClient(path=CHROMA_DIR)
    return None


def get_or_create_collection(user_id: int):
    client = get_chroma_client()
    if client:
        # One collection per user for strict multi-tenant isolation
        collection_name = f"user_{user_id}_materials"
        return client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    return None


def extract_text_by_pages(file_path: str) -> List[Dict[str, Any]]:
    """Extracts text page-by-page from a PDF or text file."""
    pages = []
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        try:
            reader = pypdf.PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages.append({"page_number": page_idx + 1, "text": text.strip()})
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
    else:
        # Plain text / markdown file
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            # If plain text is large, simulate pages (~2500 chars per page)
            page_size = 2500
            for idx in range(0, max(1, len(content)), page_size):
                page_text = content[idx : idx + page_size]
                pages.append({"page_number": (idx // page_size) + 1, "text": page_text.strip()})
        except Exception as e:
            print(f"Error reading text file {file_path}: {e}")

    return pages


def chunk_text_with_metadata(
    pages: List[Dict[str, Any]],
    filename: str,
    doc_type: str,
    user_id: int,
    chunk_size: int = 600,
    overlap: int = 100
) -> List[Dict[str, Any]]:
    """
    Splits page text into ~600 character chunks with 100 character overlap,
    attaching exact filename, page, doc_type, and user_id metadata to each chunk.
    """
    chunks = []
    step = max(50, chunk_size - overlap)

    for p in pages:
        page_num = p["page_number"]
        text = p["text"]
        if not text:
            continue

        if len(text) <= chunk_size:
            chunk_id = f"{filename}_p{page_num}_c0"
            chunks.append({
                "chunk_id": chunk_id,
                "text": text,
                "metadata": {
                    "filename": filename,
                    "doc_type": doc_type,  # 'syllabus', 'notes', 'past_paper'
                    "page": page_num,
                    "user_id": user_id
                }
            })
        else:
            c_idx = 0
            for i in range(0, len(text), step):
                chunk_slice = text[i : i + chunk_size]
                if len(chunk_slice.strip()) < 30 and i > 0:
                    continue  # skip tiny trailing fragments
                chunk_id = f"{filename}_p{page_num}_c{c_idx}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk_slice.strip(),
                    "metadata": {
                        "filename": filename,
                        "doc_type": doc_type,
                        "page": page_num,
                        "user_id": user_id
                    }
                })
                c_idx += 1

    return chunks


def index_chunks_into_vector_store(chunks: List[Dict[str, Any]], user_id: int) -> int:
    """Stores text chunks and metadata into ChromaDB vector store."""
    if not chunks:
        return 0

    collection = get_or_create_collection(user_id)
    if collection:
        ids = [c["chunk_id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        # Batch upsert to prevent size limits
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            collection.upsert(
                ids=ids[i : i + batch_size],
                documents=documents[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size]
            )
        return len(chunks)

    # In case ChromaDB client isn't available, write to a lightweight fallback JSON store
    fallback_store_path = os.path.join(CHROMA_DIR, f"user_{user_id}_fallback_store.json")
    import json
    existing = []
    if os.path.exists(fallback_store_path):
        try:
            with open(fallback_store_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []
    existing.extend(chunks)
    with open(fallback_store_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)
    return len(chunks)


def process_and_ingest_file(file_path: str, filename: str, doc_type: str, user_id: int):
    """Full pipeline: extract page text -> chunk with metadata -> vector store indexing."""
    pages = extract_text_by_pages(file_path)
    chunks = chunk_text_with_metadata(pages, filename, doc_type, user_id)
    count = index_chunks_into_vector_store(chunks, user_id)
    return {
        "page_count": len(pages),
        "chunk_count": count,
        "chunks": chunks
    }
