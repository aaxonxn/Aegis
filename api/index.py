"""
Aegis Knowledge Intelligence System — Vercel Serverless API.
Exposes evidence-first QA, canonical entity lookup, revision conflict resolution,
document provenance, and benchmark evaluation reporting via FastAPI.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from storage.database import AegisDatabase
from knowledge.entity_resolution import EntityResolver, CANONICAL_ENTITIES
from knowledge.conflict_manager import ConflictManager
from retrieval.qa_engine import AegisQAEngine

app = FastAPI(
    title="Aegis Knowledge Intelligence API",
    description="Offline-first industrial document intelligence platform for Aegis Series-7 HCS",
    version="1.0.0"
)

# Enable CORS for decoupled web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines with explicit path to SQLite database
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "aegis_knowledge.db")
db = AegisDatabase(db_path=DB_PATH)
qa_engine = AegisQAEngine(db=db)
conflict_mgr = ConflictManager()
resolver = EntityResolver()


class QueryRequest(BaseModel):
    question: str = Field(..., description="Natural language question about Aegis Series-7 HCS")


@app.get("/api/health")
def health_check() -> Dict[str, Any]:
    """Health check verifying database connectivity and chunk indexing."""
    with db.get_connection() as conn:
        doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        chunk_count = conn.execute("SELECT COUNT(*) FROM document_chunks").fetchone()[0]
        fact_count = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
    
    return {
        "status": "healthy",
        "service": "Aegis Knowledge Intelligence API",
        "runtime": "Vercel Serverless (FastAPI)",
        "database": {
            "connected": True,
            "documents_indexed": doc_count,
            "chunks_indexed": chunk_count,
            "facts_indexed": fact_count
        }
    }


@app.post("/api/query")
def ask_question(req: QueryRequest) -> Dict[str, Any]:
    """
    Execute evidence-grounded natural language question answering.
    Returns direct answer, supporting claims, granular coordinate citations,
    confidence metrics, and honest negative abstention notifications.
    """
    q = req.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
    
    try:
        response = qa_engine.answer_question(q)
        return response.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QA Engine query processing error: {str(e)}")


@app.get("/api/entities")
def list_canonical_entities() -> List[Dict[str, Any]]:
    """Return all canonical entities with alias tables and disambiguation attributes."""
    return [
        {
            "canonical_name": e.canonical_name,
            "entity_type": e.entity_type,
            "aliases": e.aliases,
            "location": e.location,
            "status": e.status,
            "description": e.description,
            "notes": e.notes
        }
        for e in CANONICAL_ENTITIES
    ]


@app.get("/api/conflicts")
def list_revision_conflicts() -> List[Dict[str, Any]]:
    """Return revision-aware conflicts and deterministic resolution rationale."""
    conflicts = conflict_mgr.get_all_conflicts()
    return [c.model_dump() for c in conflicts]


@app.get("/api/documents")
def list_documents() -> List[Dict[str, Any]]:
    """Return all 20 ingested files with format, trust level, and chunk counts."""
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT d.document_id, d.filename, d.file_format, d.doc_type, d.trust_level, d.trust_score, d.revision,
                   COUNT(c.chunk_id) as chunk_count
            FROM documents d
            LEFT JOIN document_chunks c ON d.document_id = c.document_id
            GROUP BY d.document_id
            ORDER BY d.file_format, d.filename
        """)
        rows = [dict(r) for r in cursor.fetchall()]
    return rows


@app.get("/api/benchmarks")
def get_benchmarks() -> Dict[str, Any]:
    """Return multi-phase evaluation metrics (Phase 1 baseline vs. Phase 2 robustness)."""
    return {
        "phase1_baseline": {
            "title": "Phase 1: Ground Truth Baseline Benchmark",
            "total_questions": 23,
            "accuracy_percent": 100.0,
            "citation_validity_percent": 100.0,
            "abstention_precision_percent": 100.0,
            "automated_tests_passing": 38,
            "scope": "Targeted baseline evaluation suite"
        },
        "phase2_robustness": {
            "title": "Phase 2: Independent Robustness & Generalization Audit",
            "total_questions": 45,
            "accuracy_percent": 60.0,
            "citation_validity_percent": 93.3,
            "abstention_precision_percent": 100.0,
            "unanswerable_detection_recall_percent": 60.0,
            "automated_tests_passing": 48,
            "categories": {
                "semantically_rephrased_factual": {"tested": 15, "correct": 11, "accuracy": 73.3},
                "multi_document_reasoning": {"tested": 10, "correct": 4, "accuracy": 40.0},
                "entity_disambiguation": {"tested": 5, "correct": 3, "accuracy": 60.0},
                "false_premise_handling": {"tested": 5, "correct": 3, "accuracy": 60.0},
                "unanswerable_abstention": {"tested": 5, "correct": 3, "accuracy": 60.0},
                "targeted_adversarial_scenarios": {"tested": 5, "correct": 3, "accuracy": 60.0}
            },
            "entailment_validator": {
                "total_claims": 88,
                "direct_evidence_percent": 58.0,
                "inferred_information_percent": 26.1,
                "unsupported_claims_percent": 15.9,
                "contradicted_claims_percent": 0.0
            }
        }
    }
