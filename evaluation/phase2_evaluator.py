"""
Phase 2 Robustness, Generalization & Adversarial Evaluation Runner.
Executes the 45 unseen evaluation questions against the Aegis QA engine,
validates citations, computes deep evidence entailment, calculates category-level
metrics with exact denominators, isolates failure cases, and saves structured results.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional

from storage.database import AegisDatabase
from retrieval.qa_engine import AegisQAEngine, QAResponse
from evaluation.phase2_questions import PHASE2_QUESTIONS_SPEC, Phase2EvaluationItem
from evaluation.entailment_validator import EvidenceEntailmentValidator, ResponseEntailmentReport

logger = logging.getLogger("Phase2Evaluator")


class Phase2Evaluator:
    """
    Independent robustness and generalization evaluation harness for Aegis.
    Evaluates 45 unseen questions across semantic variations, multi-doc reasoning,
    entity disambiguation, false premises, abstention, and adversarial scenarios.
    """

    def __init__(self, db: Optional[AegisDatabase] = None, qa_engine: Optional[AegisQAEngine] = None):
        self.db = db or AegisDatabase()
        self.qa_engine = qa_engine or AegisQAEngine(self.db)
        self.entailment_validator = EvidenceEntailmentValidator(self.db)
        self.dataset_files = [d.filename for d in self.db.get_all_documents()]

    def evaluate_item(self, item: Phase2EvaluationItem, response: QAResponse) -> Dict[str, Any]:
        """
        Rigorously evaluate a single Phase 2 question response.
        """
        full_text = (response.direct_answer + " " + " ".join(response.claims)).lower()

        # 1. Criteria Matching
        matched_criteria = []
        for crit in item.expected_criteria:
            crit_words = crit.lower().split()
            if crit.lower() in full_text or all(w in full_text for w in crit_words):
                matched_criteria.append(crit)

        crit_score = len(matched_criteria) / max(len(item.expected_criteria), 1)

        # 2. Correctness Determination
        is_correct = False
        failure_mode = None

        if item.expected_abstain:
            if response.abstain:
                is_correct = True
            else:
                is_correct = False
                failure_mode = "FAILED_TO_ABSTAIN_HALLUCINATION"
        elif item.is_false_premise:
            # Must detect/reject false premise or satisfy negative premise criteria
            # If the response uncritically answered without meeting false premise rejection criteria
            false_premise_rejection_markers = [
                "false premise", "incorrect assumption", "not the same", "not on hpu",
                "180 bar", "coolant loop", "skid b", "no voltage sensor", "not specified",
                "prohibited", "never", "50 bar", "no approval", "not signed", "unrelated"
            ]
            has_rejection = any(m in full_text for m in false_premise_rejection_markers)
            if has_rejection and crit_score >= 0.5:
                is_correct = True
            elif response.abstain:
                # Abstention on a false premise is acceptable if it recognizes the assumption is ungrounded
                is_correct = True
            else:
                is_correct = False
                failure_mode = "UNCRITICAL_ACCEPTANCE_OF_FALSE_PREMISE"
        else:
            # Positive factual / multi-doc question
            if response.abstain:
                is_correct = False
                failure_mode = "ERRONEOUS_ABSTENTION_ON_ANSWERABLE_QUERY"
            elif crit_score >= 0.65:
                is_correct = True
            else:
                is_correct = False
                failure_mode = "INSUFFICIENT_CRITERIA_COVERAGE"

        # 3. Citation Validation
        cited_docs = [s.get("document", "") for s in response.sources]
        expected_basenames = [os.path.basename(s).lower() for s in item.expected_sources]
        all_pkg_expected = "all package documents" in expected_basenames

        sources_valid = True
        if not response.sources:
            sources_valid = False
        else:
            for s in response.sources:
                d = s.get("document", "")
                base = os.path.basename(d).lower()
                if d == "All Package Documents":
                    if not (all_pkg_expected or item.expected_abstain):
                        sources_valid = False
                elif not any(base == os.path.basename(df).lower() for df in self.dataset_files):
                    sources_valid = False

        # 4. Deep Evidence Entailment Verification
        entailment_report = self.entailment_validator.evaluate_response_entailment(response)

        # Failure explanation
        failure_explanation = ""
        if not is_correct:
            if failure_mode == "FAILED_TO_ABSTAIN_HALLUCINATION":
                failure_explanation = (
                    f"System generated an affirmative answer with confidence '{response.confidence_status}' "
                    f"instead of abstaining. The requested property is undocumented in the package."
                )
            elif failure_mode == "UNCRITICAL_ACCEPTANCE_OF_FALSE_PREMISE":
                failure_explanation = (
                    f"Question contained an invalid assumption ('{item.variation_type}'). The system failed to "
                    f"detect or reject the false premise, producing an answer as though the premise were true."
                )
            elif failure_mode == "ERRONEOUS_ABSTENTION_ON_ANSWERABLE_QUERY":
                failure_explanation = (
                    "System erroneously abstained on an answerable question because BM25 or structured retrieval "
                    "did not find sufficient keyword overlap."
                )
            elif failure_mode == "INSUFFICIENT_CRITERIA_COVERAGE":
                missing = [c for c in item.expected_criteria if c not in matched_criteria]
                failure_explanation = (
                    f"Response failed to cover required technical facts. Missing criteria: {missing}. "
                    f"Answer was generated via fallback snippet truncation: '{response.direct_answer[:150]}...'"
                )

        return {
            "id": item.id,
            "category": item.category,
            "question": item.question,
            "variation_type": item.variation_type,
            "focus_entity": item.focus_entity,
            "expected_criteria": item.expected_criteria,
            "expected_abstain": item.expected_abstain,
            "is_false_premise": item.is_false_premise,
            "ground_truth_answer": item.ground_truth_answer,
            "actual_direct_answer": response.direct_answer,
            "claims": response.claims,
            "sources": response.sources,
            "confidence_status": response.confidence_status,
            "confidence_score": response.confidence_score,
            "actual_abstain": response.abstain,
            "is_correct": is_correct,
            "failure_mode": failure_mode,
            "failure_explanation": failure_explanation,
            "crit_score": round(crit_score, 2),
            "matched_criteria": matched_criteria,
            "sources_valid": sources_valid,
            "entailment": entailment_report.model_dump(),
            "notes": item.notes
        }

    def run_evaluation(self) -> Dict[str, Any]:
        """
        Run the complete 45-question Phase 2 evaluation benchmark and calculate all metrics.
        """
        logger.info("Executing Phase 2 Robustness & Generalization Benchmark (45 questions)...")
        results: List[Dict[str, Any]] = []

        for item in PHASE2_QUESTIONS_SPEC:
            response = self.qa_engine.answer_question(item.question)
            eval_res = self.evaluate_item(item, response)
            results.append(eval_res)

        total_questions = len(results)
        total_correct = sum(1 for r in results if r["is_correct"])
        overall_accuracy_percent = round((total_correct / total_questions) * 100.0, 1)

        # Category breakdowns
        categories = [
            "SEMANTIC_REPHRASED",
            "MULTI_DOC_REASONING",
            "ENTITY_DISAMBIGUATION",
            "FALSE_PREMISE",
            "UNANSWERABLE_ABSTENTION",
            "ADVERSARIAL"
        ]

        category_metrics = {}
        for cat in categories:
            cat_results = [r for r in results if r["category"] == cat]
            cat_total = len(cat_results)
            cat_correct = sum(1 for r in cat_results if r["is_correct"])
            cat_acc = round((cat_correct / cat_total) * 100.0, 1) if cat_total > 0 else 0.0
            category_metrics[cat] = {
                "total": cat_total,
                "correct": cat_correct,
                "accuracy_percent": cat_acc
            }

        # Variation breakdowns
        variations = sorted(list(set(r["variation_type"] for r in results)))
        variation_metrics = {}
        for var in variations:
            var_results = [r for r in results if r["variation_type"] == var]
            var_total = len(var_results)
            var_correct = sum(1 for r in var_results if r["is_correct"])
            var_acc = round((var_correct / var_total) * 100.0, 1) if var_total > 0 else 0.0
            variation_metrics[var] = {
                "total": var_total,
                "correct": var_correct,
                "accuracy_percent": var_acc
            }

        # Entailment aggregations across all claims
        all_claims_count = sum(r["entailment"]["claims_count"] for r in results)
        total_direct_evidence = sum(r["entailment"]["direct_evidence_count"] for r in results)
        total_inferred = sum(r["entailment"]["inferred_count"] for r in results)
        total_unsupported = sum(r["entailment"]["unsupported_count"] for r in results)
        total_contradicted = sum(r["entailment"]["contradicted_count"] for r in results)

        direct_rate = round((total_direct_evidence / max(all_claims_count, 1)) * 100.0, 1)
        inferred_rate = round((total_inferred / max(all_claims_count, 1)) * 100.0, 1)
        unsupported_rate = round((total_unsupported / max(all_claims_count, 1)) * 100.0, 1)
        contradicted_rate = round((total_contradicted / max(all_claims_count, 1)) * 100.0, 1)

        # Collect failure cases
        failures = [r for r in results if not r["is_correct"]]

        summary = {
            "total_questions": total_questions,
            "total_correct": total_correct,
            "overall_accuracy_percent": overall_accuracy_percent,
            "category_metrics": category_metrics,
            "variation_metrics": variation_metrics,
            "entailment_summary": {
                "total_claims": all_claims_count,
                "direct_evidence": total_direct_evidence,
                "direct_evidence_percent": direct_rate,
                "inferred": total_inferred,
                "inferred_percent": inferred_rate,
                "unsupported": total_unsupported,
                "unsupported_percent": unsupported_rate,
                "contradicted": total_contradicted,
                "contradicted_percent": contradicted_rate,
                "supported_or_inferred_percent": round(direct_rate + inferred_rate, 1)
            },
            "failures_count": len(failures),
            "failures": failures,
            "results": results
        }

        # Save structured results to file
        output_path = "data/processed/phase2_evaluation_results.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return summary

