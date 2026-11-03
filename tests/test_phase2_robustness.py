"""
Automated Test Suite for Phase 2 Independent Robustness, Generalization & Entailment Validation.
Validates:
1. Dataset specifications (>=40 unseen questions, category distributions, no Q1-Q23 verbatim duplication).
2. Evidence entailment validator (direct evidence, inferred evidence, unsupported claims, numerical contradictions, entity collisions).
3. Phase 2 evaluator execution, metric calculation, denominator precision, and structured result exports.
4. Preservation and invariance of the original 23-question benchmark and database state.
"""

import os
import sys
import json
import pytest

# Ensure workspace root in path
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from storage.database import AegisDatabase
from retrieval.qa_engine import AegisQAEngine, QAResponse
from evaluation.questions import EVALUATION_QUESTIONS_SPEC
from evaluation.evaluator import AegisEvaluator
from evaluation.phase2_questions import PHASE2_QUESTIONS_SPEC, Phase2EvaluationItem
from evaluation.entailment_validator import EvidenceEntailmentValidator, ClaimEntailmentResult
from evaluation.phase2_evaluator import Phase2Evaluator


@pytest.fixture(scope="module")
def db():
    return AegisDatabase()


@pytest.fixture(scope="module")
def qa_engine(db):
    return AegisQAEngine(db)


@pytest.fixture(scope="module")
def entailment_validator(db):
    return EvidenceEntailmentValidator(db)


@pytest.fixture(scope="module")
def phase2_evaluator(db, qa_engine):
    return Phase2Evaluator(db, qa_engine)


# -----------------------------------------------------------------------------
# 1. Phase 2 Dataset Specification & Quality Tests
# -----------------------------------------------------------------------------
def test_phase2_dataset_size_and_categories():
    """Verify Phase 2 dataset contains at least 40 new questions with required category breakdown."""
    total_q = len(PHASE2_QUESTIONS_SPEC)
    assert total_q >= 40, f"Expected at least 40 questions, got {total_q}"

    cat_counts = {}
    for item in PHASE2_QUESTIONS_SPEC:
        cat_counts[item.category] = cat_counts.get(item.category, 0) + 1

    assert cat_counts.get("SEMANTIC_REPHRASED", 0) >= 15
    assert cat_counts.get("MULTI_DOC_REASONING", 0) >= 10
    assert cat_counts.get("ENTITY_DISAMBIGUATION", 0) >= 5
    assert cat_counts.get("FALSE_PREMISE", 0) >= 5
    assert cat_counts.get("UNANSWERABLE_ABSTENTION", 0) >= 5
    assert cat_counts.get("ADVERSARIAL", 0) >= 5


def test_no_exact_wording_duplication_with_original_benchmark():
    """Verify no Phase 2 question duplicates the exact wording of the original 23 questions."""
    original_questions = {item.question.strip().lower() for item in EVALUATION_QUESTIONS_SPEC}
    for item in PHASE2_QUESTIONS_SPEC:
        q_clean = item.question.strip().lower()
        assert q_clean not in original_questions, f"Duplicate question detected: {item.question}"


def test_phase2_variation_coverage():
    """Verify semantic generalization covers terminology, conversational, abbreviations, indirect, misspellings."""
    variations = {item.variation_type for item in PHASE2_QUESTIONS_SPEC}
    expected_vars = {"conversational", "terminology", "abbreviation", "indirect", "misspelling", "combined_facts", "cross_doc"}
    assert expected_vars.issubset(variations), f"Missing expected variation types: {expected_vars - variations}"


# -----------------------------------------------------------------------------
# 2. Evidence Entailment Validator Unit Tests
# -----------------------------------------------------------------------------
def test_entailment_validator_direct_evidence(entailment_validator):
    """A claim matching cited chunk facts must be classified as DIRECT_EVIDENCE."""
    source_info = {
        "document": "manuals/operator_manual.pdf",
        "location": "Section 4.3, Page 1",
        "extraction_method": "pymupdf_text",
        "trust_level": "OFFICIAL"
    }
    claim = "Hydraulic fluid level must be within the normal band on the sight glass."
    result = entailment_validator.evaluate_claim(claim_id=1, claim_text=claim, source_info=source_info)
    
    assert result.entailment_status == "DIRECT_EVIDENCE"
    assert result.entailment_score >= 0.7
    assert result.entity_alignment is True
    assert result.numerical_consistency is True


def test_entailment_validator_entity_collision_detection(entailment_validator):
    """Asserting facts about PS-40 against a PS-04 chunk must flag entity collision / contradiction."""
    source_info = {
        "document": "manuals/operator_manual.pdf",
        "location": "Section 5, Page 1",
        "extraction_method": "pymupdf_text",
        "trust_level": "OFFICIAL"
    }
    # Claim incorrectly maps PS-40 to the HPU discharge line
    contradictory_claim = "Pressure sensor PS-40 monitors the HPU discharge pressure on Skid A."
    result = entailment_validator.evaluate_claim(claim_id=2, claim_text=contradictory_claim, source_info=source_info)
    
    assert result.entailment_status == "CONTRADICTED"
    assert result.entity_alignment is False


def test_entailment_validator_numerical_contradiction(entailment_validator):
    """Claiming 200 bar when chunk states 180 bar must trigger contradiction."""
    source_info = {
        "document": "manuals/legacy_manual_v1.html",
        "location": "Section 5",
        "extraction_method": "bs4_html",
        "trust_level": "OFFICIAL_SUPERSEDED"
    }
    contradictory_claim = "Under legacy manual v1, normal operating pressure was 200 bar."
    result = entailment_validator.evaluate_claim(claim_id=3, claim_text=contradictory_claim, source_info=source_info)
    
    assert result.entailment_status == "CONTRADICTED"
    assert result.numerical_consistency is False


def test_entailment_validator_missing_citation(entailment_validator):
    """A claim with no source citation must be classified as UNSUPPORTED."""
    claim = "Some completely unsubstantiated claim about unlisted machinery."
    result = entailment_validator.evaluate_claim(claim_id=4, claim_text=claim, source_info=None)
    
    assert result.entailment_status == "UNSUPPORTED"
    assert result.entailment_score == 0.0


def test_entailment_validator_exhaustive_search_abstention(entailment_validator):
    """Verified absence across 'All Package Documents' is properly handled."""
    source_info = {
        "document": "All Package Documents",
        "location": "Exhaustive review",
        "extraction_method": "exhaustive_absence_verification",
        "trust_level": "OFFICIAL"
    }
    claim = "Thermal operating limits are absent from the provided package."
    result = entailment_validator.evaluate_claim(claim_id=5, claim_text=claim, source_info=source_info)
    
    assert result.entailment_status == "DIRECT_EVIDENCE"
    assert result.entailment_score == 1.0


# -----------------------------------------------------------------------------
# 3. Phase 2 Evaluator & Reporting Tests
# -----------------------------------------------------------------------------
def test_phase2_evaluator_execution_and_exports(phase2_evaluator):
    """Run evaluation and verify structured outputs and metrics integrity."""
    summary = phase2_evaluator.run_evaluation()
    
    assert summary["total_questions"] == 45
    assert "overall_accuracy_percent" in summary
    assert "category_metrics" in summary
    assert "entailment_summary" in summary
    assert "failures" in summary
    
    # Check export file exists
    export_path = "data/processed/phase2_evaluation_results.json"
    assert os.path.exists(export_path)
    assert os.path.getsize(export_path) > 10000


# -----------------------------------------------------------------------------
# 4. Invariance & Non-Regression of Original Benchmark
# -----------------------------------------------------------------------------
def test_original_23_question_benchmark_invariance(db, qa_engine):
    """The original 23-question benchmark must remain untouched and report 100% accuracy."""
    assert len(EVALUATION_QUESTIONS_SPEC) == 23
    evaluator = AegisEvaluator(db, qa_engine)
    summary = evaluator.run_evaluation()
    assert summary["accuracy_percent"] == 100.0
    assert summary["questions_correct"] == 23

