"""
Unit tests for Aegis Evaluation Framework Improvements.
Validates:
1. Incorrect abstention (positive question fails if model abstains; negative question fails if model does not abstain).
2. Correct abstention (negative questions pass when model abstains).
3. Missing citations (empty sources list fails validity).
4. Incorrect source documents (fabricated/non-existent documents fail validity).
5. Citations pointing to unrelated evidence (existing file like SDS fails grounding when cited for HPU operating pressure).
6. Semantically equivalent questions with different wording.
7. Distinct evaluation metrics and denominator precision.
"""

import os
import sys
import pytest
from typing import Dict, Any

# Ensure workspace root in path
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from storage.database import AegisDatabase
from retrieval.qa_engine import AegisQAEngine, QAResponse
from evaluation.questions import EvaluationItem, EVALUATION_QUESTIONS_SPEC
from evaluation.evaluator import AegisEvaluator


@pytest.fixture(scope="module")
def db():
    return AegisDatabase()


@pytest.fixture(scope="module")
def qa_engine(db):
    return AegisQAEngine(db)


@pytest.fixture(scope="module")
def evaluator(db, qa_engine):
    return AegisEvaluator(db, qa_engine)


# -----------------------------------------------------------------------------
# 1. Correctness Calculation & Abstention Logic Tests
# -----------------------------------------------------------------------------
def test_incorrect_abstention_on_positive_question_fails(evaluator):
    """
    If expected_abstain=False, but the response has abstain=True,
    the evaluation MUST fail even if keyword criteria appear in the text.
    """
    item = EvaluationItem(
        id=991,
        question="What must be true before starting the Hydraulic Power Unit?",
        expected_criteria=["fluid level normal", "iv-21 open", "emergency stop reset", "maintenance panel closed"],
        expected_abstain=False,
        expected_sources=["operator_manual.pdf"],
        focus_entity="HPU"
    )

    # Response erroneously abstains, although it includes all matching words
    erroneous_response = QAResponse(
        question=item.question,
        direct_answer="I cannot verify whether fluid level normal, iv-21 open, emergency stop reset, and maintenance panel closed are met.",
        claims=["fluid level normal", "iv-21 open", "emergency stop reset", "maintenance panel closed"],
        sources=[{"document": "manuals/operator_manual.pdf", "location": "Section 4.3, Page 1", "extraction_method": "pymupdf_text", "trust_level": "OFFICIAL"}],
        confidence_status="UNANSWERABLE / ABSTAIN",
        confidence_score=0.0,
        abstain=True  # Incorrect abstention on positive question
    )

    eval_result = evaluator.evaluate_response(item, erroneous_response)
    assert eval_result["is_correct"] is False, "Response with abstain=True on positive question must fail correctness."
    assert eval_result["abstention_correct"] is False, "Abstention decision must be flagged as mismatch."


def test_incorrect_non_abstention_on_negative_question_fails(evaluator):
    """
    If expected_abstain=True, but the response has abstain=False,
    the evaluation MUST fail even if criteria keywords ('not specified') are present.
    """
    item = EvaluationItem(
        id=992,
        question="What is the maximum continuous operating temperature of PS-04A?",
        expected_criteria=["not specified", "not documented"],
        expected_abstain=True,
        expected_sources=["All Package Documents"],
        focus_entity="PS-04A"
    )

    # Response fails to set abstain=True, despite having the words 'not specified'
    hallucinated_response = QAResponse(
        question=item.question,
        direct_answer="The temperature is not specified and not documented in Section 2.",
        claims=["Temperature is 85C."],
        sources=[{"document": "manuals/operator_manual.pdf", "location": "Section 2, Page 1", "extraction_method": "pymupdf_text", "trust_level": "OFFICIAL"}],
        confidence_status="HIGH",
        confidence_score=0.9,
        abstain=False  # Erroneously failed to abstain
    )

    eval_result = evaluator.evaluate_response(item, hallucinated_response)
    assert eval_result["is_correct"] is False, "Response with abstain=False on unanswerable question must fail correctness."
    assert eval_result["abstention_correct"] is False, "Abstention decision must be flagged as mismatch."


def test_correct_abstention_passes(evaluator):
    """
    If expected_abstain=True and response has abstain=True,
    the evaluation passes.
    """
    item = EvaluationItem(
        id=993,
        question="Who approved engineering bulletin ECN-1058?",
        expected_criteria=["not specified", "not documented"],
        expected_abstain=True,
        expected_sources=["ECN-1058.pdf"],
        focus_entity="ECN-1058"
    )

    valid_abstain_response = QAResponse(
        question=item.question,
        direct_answer="The documentation does not state who approved ECN-1058; the approver block is omitted.",
        claims=["Approver identity for ECN-1058 is absent."],
        sources=[{"document": "engineering_bulletins/ECN-1058.pdf", "location": "Page 1 Header Block", "extraction_method": "pymupdf_text", "trust_level": "AUTHORITATIVE_BULLETIN"}],
        confidence_status="UNANSWERABLE / ABSTAIN",
        confidence_score=0.0,
        abstain=True
    )

    eval_result = evaluator.evaluate_response(item, valid_abstain_response)
    assert eval_result["is_correct"] is True
    assert eval_result["abstention_correct"] is True


# -----------------------------------------------------------------------------
# 2. Citation & Evidence Grounding Tests
# -----------------------------------------------------------------------------
def test_missing_citations_fails_validity(evaluator):
    """
    A response with empty sources must fail document validity and evidence grounding.
    """
    item = EvaluationItem(
        id=994,
        question="What is the current normal operating pressure for the HPU?",
        expected_criteria=["200 bar", "revision 3.2"],
        expected_abstain=False,
        expected_sources=["operator_manual.pdf", "ECN-1042.pdf"],
        focus_entity="HPU"
    )

    response_no_sources = QAResponse(
        question=item.question,
        direct_answer="The operating pressure is 200 bar on revision 3.2.",
        claims=["200 bar setpoint."],
        sources=[],  # Missing citations
        confidence_status="HIGH",
        confidence_score=0.95,
        abstain=False
    )

    cite_check = evaluator.verify_citation(item, response_no_sources)
    assert cite_check["doc_valid"] is False, "Empty sources must fail document validity."
    assert cite_check["grounding_valid"] is False, "Empty sources must fail evidence grounding."
    assert "Missing citations" in cite_check["reason"]


def test_incorrect_source_documents_fails(evaluator):
    """
    A response citing a non-existent document must fail document validity and grounding.
    """
    item = EvaluationItem(
        id=995,
        question="What does alarm A17 indicate?",
        expected_criteria=["low hydraulic pressure"],
        expected_abstain=False,
        expected_sources=["alarm_reference.pdf"],
        focus_entity="A17"
    )

    response_fake_source = QAResponse(
        question=item.question,
        direct_answer="Alarm A17 indicates low hydraulic pressure.",
        claims=["Low hydraulic pressure below 150 bar."],
        sources=[{"document": "fabricated_alarm_spec_2026.pdf", "location": "Page 12", "extraction_method": "pymupdf_text", "trust_level": "UNKNOWN"}],
        confidence_status="HIGH",
        confidence_score=0.9,
        abstain=False
    )

    cite_check = evaluator.verify_citation(item, response_fake_source)
    assert cite_check["doc_valid"] is False, "Fabricated document must fail document validity."
    assert cite_check["grounding_valid"] is False, "Fabricated document must fail evidence grounding."
    assert "do not exist" in cite_check["reason"]


def test_citations_pointing_to_unrelated_evidence(evaluator):
    """
    Distinguishes document existence from actual evidence grounding:
    Safety Data Sheet (safety_data_sheet_hydraulic_fluid.pdf) exists in the dataset,
    so doc_valid=True. But when cited for HPU operating pressure or alarm A17,
    it is not in expected_sources and lacks grounding in the topic, so grounding_valid=False.
    """
    item = EvaluationItem(
        id=996,
        question="What is the current normal operating pressure for the HPU, and under what conditions does that apply?",
        expected_criteria=["200 bar", "revision 3.2"],
        expected_abstain=False,
        expected_sources=["operator_manual.pdf", "ECN-1042.pdf", "configuration_export.json"],
        focus_entity="HPU"
    )

    # Citing Safety Data Sheet for HPU operating pressure
    response_unrelated_source = QAResponse(
        question=item.question,
        direct_answer="The current normal operating pressure is 200 bar on revision 3.2.",
        claims=["200 bar applies to software revision 3.2."],
        sources=[
            {
                "document": "safety_data_sheet_hydraulic_fluid.pdf",  # Real file in dataset, but unrelated to 200 bar setpoint
                "location": "Section 9 (Physical and Chemical Properties), Page 2",
                "extraction_method": "pymupdf_text",
                "trust_level": "OFFICIAL"
            }
        ],
        confidence_status="HIGH",
        confidence_score=0.9,
        abstain=False
    )

    cite_check = evaluator.verify_citation(item, response_unrelated_source)
    assert cite_check["doc_valid"] is True, "SDS file exists in dataset, so doc_valid must be True."
    assert cite_check["grounding_valid"] is False, "SDS is unrelated to operating pressure; grounding_valid must be False."
    assert "not match expected" in cite_check["reason"] or "not grounded" in cite_check["reason"]


# -----------------------------------------------------------------------------
# 3. Semantically Equivalent Questions Tests
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("rephrased_q,expected_substr,expected_abstain", [
    ("What preconditions are required before turning on the HPU?", "fluid level", False),
    ("What is the normal operating pressure of the HPU right now, and which firmware does that require?", "200 bar", False),
    ("Why is alarm A17 triggered and what are its causes?", "low hydraulic pressure", False),
    ("Are component PS-04 and component PS-04A identical?", "not the same", False),
    ("Which document replaced sensor PS-04 with PS-04A?", "ecn-1042", False),
    ("When is resetting the controller prohibited?", "50 bar", False),
    ("Where is isolation valve IV-21 installed according to the component register?", "hydraulic module", False),
    ("Are PS-04 and PS-40 the same part?", "not the same", False),
    ("What is the thermal operating limit for sensor PS-04A?", "not specify", True),
    ("How often should the voltage sensor in the electrical schematic be calibrated?", "not provide", True),
    ("Which engineer signed off on bulletin ECN-1058?", "not state", True),
    ("What is the failure rate or MTBF metric for isolation valve IV-21?", "not provide", True),
    ("Can the Aegis Series-7 run on 400V 3-phase electricity?", "not establish", True),
])
def test_semantically_equivalent_questions(qa_engine, rephrased_q, expected_substr, expected_abstain):
    """
    Verifies that questions phrased differently from benchmark wording still route
    to the correct grounded knowledge or honest abstention decisions.
    """
    resp = qa_engine.answer_question(rephrased_q)
    assert resp.abstain == expected_abstain, f"Abstention mismatch on query: '{rephrased_q}'"
    full_text = (resp.direct_answer + " " + " ".join(resp.claims)).lower()
    assert expected_substr.lower() in full_text, f"Expected '{expected_substr}' in response for: '{rephrased_q}'"
    assert len(resp.sources) > 0, "Response must include citations."


# -----------------------------------------------------------------------------
# 4. Evaluation Metrics & Denominators Precision Test
# -----------------------------------------------------------------------------
def test_evaluation_metrics_and_denominators(evaluator):
    """
    Executes benchmark evaluation and validates exact denominators and separate metric calculations:
    - Overall accuracy: 23 questions
    - Positive accuracy: 18 questions (Q1–Q18)
    - Negative abstention accuracy: 5 questions (Q19–Q23)
    - Document validity: 23 questions
    - Grounding validity: 23 questions
    - Coverage: 23 questions
    """
    summary = evaluator.run_evaluation()

    assert summary["total_questions"] == 23
    assert summary["positive_questions_total"] == 18
    assert summary["negative_questions_total"] == 5
    assert summary["positive_questions_total"] + summary["negative_questions_total"] == summary["total_questions"]

    # Verify denominator arithmetic
    expected_overall_acc = round((summary["questions_correct"] / 23) * 100.0, 1)
    expected_pos_acc = round((summary["positive_questions_correct"] / 18) * 100.0, 1)
    expected_neg_acc = round((summary["negative_questions_correct"] / 5) * 100.0, 1)
    expected_doc_val = round((summary["valid_citation_documents"] / 23) * 100.0, 1)
    expected_ground_val = round((summary["valid_grounded_evidence"] / 23) * 100.0, 1)
    expected_cov = round((summary["covered_questions"] / 23) * 100.0, 1)

    assert summary["accuracy_percent"] == expected_overall_acc
    assert summary["positive_accuracy_percent"] == expected_pos_acc
    assert summary["negative_abstention_accuracy_percent"] == expected_neg_acc
    assert summary["citation_document_validity_percent"] == expected_doc_val
    assert summary["evidence_grounding_validity_percent"] == expected_ground_val
    assert summary["coverage_percent"] == expected_cov

    # Check that results file and markdown report exist and are non-empty
    assert os.path.exists("data/processed/evaluation_results.json")
    assert os.path.exists("reports/evaluation_report.md")
    assert os.path.getsize("data/processed/evaluation_results.json") > 5000
    assert os.path.getsize("reports/evaluation_report.md") > 5000

