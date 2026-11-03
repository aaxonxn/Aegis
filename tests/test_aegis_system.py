"""
Comprehensive Unit Test Suite for the Aegis Knowledge Intelligence System.
Validates schemas, database persistence, ingestion, entity resolution,
conflict handling, evidence-first QA, honest abstention, and evaluation harness.
"""

import os
import sys
import pytest

# Ensure workspace root in path
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from storage.database import AegisDatabase
from storage.models import Document, DocumentChunk, Entity, Fact, Relationship, Conflict
from knowledge.entity_resolution import EntityResolver, CANONICAL_ENTITIES
from knowledge.conflict_manager import ConflictManager
from retrieval.bm25_retriever import BM25Retriever
from retrieval.structured_retriever import StructuredRetriever
from retrieval.qa_engine import AegisQAEngine
from evaluation.evaluator import AegisEvaluator


@pytest.fixture(scope="module")
def db():
    database = AegisDatabase()
    return database


@pytest.fixture(scope="module")
def resolver():
    return EntityResolver()


@pytest.fixture(scope="module")
def conflict_mgr():
    return ConflictManager()


@pytest.fixture(scope="module")
def qa_engine(db):
    return AegisQAEngine(db)


# -----------------------------------------------------------------------------
# 1. Database & Schema Tests
# -----------------------------------------------------------------------------
def test_database_initialization(db):
    stats = db.get_statistics()
    assert stats["document_count"] == 20
    assert stats["chunk_count"] >= 350
    assert stats["entity_count"] >= 15
    assert stats["fact_count"] >= 30
    assert stats["relationship_count"] >= 8
    assert stats["conflict_count"] >= 4


def test_normalized_json_exports():
    kg_path = "data/processed/knowledge_graph.json"
    facts_path = "data/processed/facts_export.json"
    assert os.path.exists(kg_path), f"Missing {kg_path}"
    assert os.path.exists(facts_path), f"Missing {facts_path}"
    assert os.path.getsize(kg_path) > 10000
    assert os.path.getsize(facts_path) > 20000


# -----------------------------------------------------------------------------
# 2. Entity Resolution & Strict Disambiguation Tests
# -----------------------------------------------------------------------------
def test_entity_resolution_ps04_vs_ps04a(resolver):
    same, rationale = resolver.compare_components("PS-04", "PS-04A")
    assert same is False
    assert "NOT the same component" in rationale
    assert "ECN-1042" in rationale


def test_entity_resolution_ps04_vs_ps40(resolver):
    same, rationale = resolver.compare_components("PS-04", "PS-40")
    assert same is False
    assert "completely separate components" in rationale
    assert "Coolant Loop" in rationale


def test_entity_resolution_ps04a_vs_screenshot_label(resolver):
    same, rationale = resolver.compare_components("PS-04A", "P.S. 04-A")
    assert same is True
    assert "P.S. 04-A" in rationale
    assert "Diagnostics screen" in rationale


def test_entity_resolution_hpu_aliases(resolver):
    e1 = resolver.resolve("Hydraulic Power Unit")
    e2 = resolver.resolve("HP unit")
    e3 = resolver.resolve("Hydraulic Power Pack")
    assert e1 is not None
    assert e2 is not None
    assert e3 is not None
    assert e1.entity_id == "HPU"
    assert e2.entity_id == "HPU"
    assert e3.entity_id == "HPU"


# -----------------------------------------------------------------------------
# 3. Conflict & Revision Manager Tests
# -----------------------------------------------------------------------------
def test_conflict_manager_operating_pressure(conflict_mgr):
    conf = conflict_mgr.get_conflict_for_topic("Operating Pressure")
    assert conf is not None
    assert conf.resolution_status == "VERSION_SCOPED"
    assert "200 bar" in conf.resolution_rationale
    assert "180 bar" in conf.resolution_rationale


def test_conflict_manager_sensor_supersession(conflict_mgr):
    conf = conflict_mgr.get_conflict_for_topic("Pressure Sensor Active Model")
    assert conf is not None
    assert conf.resolution_status == "SUPERSEDED_BY_ECN"


# -----------------------------------------------------------------------------
# 4. Retrieval & QA Engine Tests
# -----------------------------------------------------------------------------
def test_qa_startup_requirements(qa_engine):
    resp = qa_engine.answer_question("What must be true before starting the Hydraulic Power Unit?")
    assert resp.abstain is False
    assert resp.confidence_status == "HIGH"
    assert len(resp.sources) >= 2
    full_text = (resp.direct_answer + " " + " ".join(resp.claims)).lower()
    assert "fluid level" in full_text
    assert "iv-21" in full_text
    assert "emergency stop" in full_text
    assert "maintenance" in full_text or "panel" in full_text


def test_qa_operating_pressure_current(qa_engine):
    resp = qa_engine.answer_question("What is the current normal operating pressure for the HPU, and under what conditions does that apply?")
    assert resp.abstain is False
    assert "200 bar" in resp.direct_answer
    assert "3.2" in resp.direct_answer


def test_qa_alarm_a17(qa_engine):
    resp = qa_engine.answer_question("What does alarm A17 indicate, and what are its possible causes?")
    assert resp.abstain is False
    assert "150 bar" in resp.direct_answer or "pressure low" in resp.direct_answer.lower()
    assert len(resp.claims) >= 3


def test_qa_hydraulic_schematic_connections(qa_engine):
    resp = qa_engine.answer_question("Which components connect directly to the HCS controller, according to the hydraulic schematic?")
    assert resp.abstain is False
    full_text = (resp.direct_answer + " " + " ".join(resp.claims)).lower()
    assert "ps-04a" in full_text
    assert "iv-21" in full_text
    assert "grey line" in full_text or "anomalous" in full_text or "review" in full_text


# -----------------------------------------------------------------------------
# 5. Negative Knowledge & Honest Abstention Tests
# -----------------------------------------------------------------------------
def test_qa_abstain_mtbf_iv21(qa_engine):
    resp = qa_engine.answer_question("What is the mean time between failures for the isolation valve IV-21?")
    assert resp.abstain is True
    assert "UNANSWERABLE" in resp.confidence_status
    assert resp.confidence_score == 0.0


def test_qa_abstain_operating_temperature(qa_engine):
    resp = qa_engine.answer_question("What is the maximum continuous operating temperature of PS-04A?")
    assert resp.abstain is True
    assert "UNANSWERABLE" in resp.confidence_status


def test_qa_abstain_voltage_sensor(qa_engine):
    resp = qa_engine.answer_question("What is the calibration interval for the electrical system diagram's voltage sensor?")
    assert resp.abstain is True
    assert "UNANSWERABLE" in resp.confidence_status


def test_qa_abstain_ecn1058_approver(qa_engine):
    resp = qa_engine.answer_question("Who approved engineering bulletin ECN-1058?")
    assert resp.abstain is True
    assert "UNANSWERABLE" in resp.confidence_status


def test_qa_abstain_400v_compatibility(qa_engine):
    resp = qa_engine.answer_question("Is the Aegis Series-7 HCS compatible with a 3-phase 400V supply?")
    assert resp.abstain is True
    assert "UNANSWERABLE" in resp.confidence_status


# -----------------------------------------------------------------------------
# 6. Evaluation Harness Integration Test
# -----------------------------------------------------------------------------
def test_evaluation_harness_execution(db, qa_engine):
    evaluator = AegisEvaluator(db, qa_engine)
    summary = evaluator.run_evaluation()
    assert summary["total_questions"] == 23
    assert summary["accuracy_percent"] == 100.0
    assert summary["citation_validity_percent"] == 100.0
    assert summary["abstention_accuracy_percent"] == 100.0
    assert summary["coverage_percent"] == 100.0

