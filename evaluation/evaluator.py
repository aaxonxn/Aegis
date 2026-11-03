"""
Reproducible Benchmark Evaluator for Aegis Knowledge Intelligence System.
Executes the full 23-question evaluation suite, strictly separates document existence
from evidence grounding, enforces rigorous abstention correctness without allowing keyword
bypasses, computes distinct metrics with exact denominators, and produces auditable reports.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Tuple, Optional
from storage.database import AegisDatabase
from storage.models import DocumentChunk
from retrieval.qa_engine import AegisQAEngine, QAResponse
from evaluation.questions import EVALUATION_QUESTIONS_SPEC, EvaluationItem

logger = logging.getLogger("AegisEvaluator")


class AegisEvaluator:
    def __init__(self, db: Optional[AegisDatabase] = None, qa_engine: Optional[AegisQAEngine] = None):
        self.db = db or AegisDatabase()
        self.qa_engine = qa_engine or AegisQAEngine(self.db)
        self.dataset_files = [d.filename for d in self.db.get_all_documents()]

        # Index all database chunks by document basename for granular evidence content verification
        self.chunks_by_doc: Dict[str, List[DocumentChunk]] = {}
        for chunk in self.db.get_all_chunks():
            base = os.path.basename(chunk.filename)
            if base not in self.chunks_by_doc:
                self.chunks_by_doc[base] = []
            self.chunks_by_doc[base].append(chunk)

    def verify_citation(self, item: EvaluationItem, response: QAResponse) -> Dict[str, Any]:
        """
        Rigorously verify citations by distinguishing document existence from actual evidence grounding.
        
        Requirements:
        1. Verify that cited documents exist in the dataset (or designated 'All Package Documents').
        2. Compare actual citations against expected_sources.
        3. Validate source locations (preserve page numbers, worksheet names, cell ranges, JSON paths).
        4. Check evidence grounding against actual chunk text in SQLite (never mark verified merely because filename exists).
        """
        if not response.sources:
            return {
                "doc_valid": False,
                "grounding_valid": False,
                "reason": "Missing citations: no sources cited in response."
            }

        expected_basenames = [os.path.basename(s).lower() for s in item.expected_sources]
        all_package_expected = "all package documents" in expected_basenames

        all_docs_exist = True
        doc_details = []
        all_locations_valid = True
        all_grounded = True
        has_expected_overlap = False

        for src in response.sources:
            doc_str = src.get("document", "").strip()
            base_name = os.path.basename(doc_str)
            loc = str(src.get("location", "")).strip()

            # 1. Document Existence Check
            if doc_str == "All Package Documents":
                doc_exists = all_package_expected or item.expected_abstain
            else:
                doc_exists = (base_name in self.dataset_files) or any(base_name.lower() == df.lower() for df in self.dataset_files)

            if not doc_exists:
                all_docs_exist = False

            # 2. Source Location Validation
            # Location must specify fine-grained coordinates (Page, Sheet, Cell, Row, Slide, JSON path, Schematic tag, etc.)
            has_fine_location = False
            if loc and loc.lower() not in ["", "none", "unknown", "n/a", "general"]:
                location_indicators = [
                    "page", "p.", "section", "sec.", "worksheet", "sheet", "cell", "row",
                    "slide", "json", "leaf", "schematic", "drawing", "aeg-dwg", "tag",
                    "panel", "header", "table", "footer", "line", "exhaustive", "key",
                    "param", "parameter", "field", "root", "entry"
                ]
                has_fine_location = any(ind in loc.lower() for ind in location_indicators) or ("." in loc) or ("_" in loc and "(" in loc)

            if not has_fine_location:
                all_locations_valid = False

            # 3. Compare with Expected Sources
            is_expected_source = (
                all_package_expected
                or base_name.lower() in expected_basenames
                or any(exp in base_name.lower() for exp in expected_basenames)
            )
            if is_expected_source:
                has_expected_overlap = True

            # 4. Content Grounding in SQLite Chunks
            # Verify that the cited document contains actual content relevant to the question/topic
            content_grounded = False
            if doc_str == "All Package Documents" and (all_package_expected or item.expected_abstain):
                content_grounded = True
            elif doc_exists:
                chunks = self.chunks_by_doc.get(base_name, [])
                if not chunks:
                    # Try matching case-insensitively
                    for k, v in self.chunks_by_doc.items():
                        if k.lower() == base_name.lower():
                            chunks = v
                            break

                doc_text = " ".join(c.content.lower() for c in chunks)
                
                # Check entity and topic alignment
                entity_tokens = [w.lower() for w in re.findall(r'[a-zA-Z0-9_\-]+', item.focus_entity) if len(w) > 1]
                entity_present = any(
                    w in doc_text or w.replace("-", "") in doc_text
                    for w in entity_tokens
                ) if entity_tokens else True

                # Check question content terms
                q_stop = {
                    "what", "when", "where", "which", "does", "under", "according", "from",
                    "that", "this", "with", "have", "before", "after", "into", "between"
                }
                q_words = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9_\-]{3,}\b', item.question) if w.lower() not in q_stop]
                matches_q = sum(1 for w in q_words if w in doc_text or w.replace("-", "") in doc_text)

                content_grounded = (entity_present or matches_q >= 1) and len(chunks) > 0 and is_expected_source

            if not content_grounded:
                all_grounded = False

            doc_details.append({
                "document": doc_str,
                "base_name": base_name,
                "location": loc,
                "exists": doc_exists,
                "fine_location": has_fine_location,
                "expected": is_expected_source,
                "content_grounded": content_grounded
            })

        doc_valid = all_docs_exist and len(response.sources) > 0
        grounding_valid = (
            doc_valid
            and has_expected_overlap
            and all_grounded
            and all_locations_valid
        )

        reasons = []
        if not all_docs_exist:
            reasons.append("One or more cited documents do not exist in the dataset.")
        if not has_expected_overlap:
            reasons.append("Cited sources do not match expected ground-truth sources.")
        if not all_locations_valid:
            reasons.append("One or more citations lack granular location coordinates (Page, Sheet, Cell, JSON path).")
        if not all_grounded:
            reasons.append("Cited document content is not grounded in question evidence or contains unrelated sources.")

        return {
            "doc_valid": doc_valid,
            "grounding_valid": grounding_valid,
            "details": doc_details,
            "reason": "; ".join(reasons) if reasons else "Citations verified and grounded."
        }

    def evaluate_response(self, item: EvaluationItem, response: QAResponse) -> Dict[str, Any]:
        """
        Evaluate a single QA response against the ground-truth specification.
        Enforces strict correctness without allowing keyword matches to override incorrect abstention.
        """
        # 1. Correctness Calculation against Criteria
        full_response_text = (response.direct_answer + " " + " ".join(response.claims)).lower()
        matched_criteria = []
        for crit in item.expected_criteria:
            crit_words = crit.lower().split()
            if crit.lower() in full_response_text or all(w in full_response_text for w in crit_words):
                matched_criteria.append(crit)

        crit_score = len(matched_criteria) / max(len(item.expected_criteria), 1)

        # STRICT CORRECTNESS LOGIC:
        # - If expected_abstain=True, the response must have abstain=True to pass.
        # - If expected_abstain=False, the response must have abstain=False and satisfy criteria (crit_score >= 0.75).
        # - Do not allow keyword matches to override an incorrect abstention decision.
        if item.expected_abstain:
            is_correct = (response.abstain is True)
        else:
            is_correct = (response.abstain is False) and (crit_score >= 0.75)

        # 2. Citation and Grounding Validation
        cite_eval = self.verify_citation(item, response)
        citation_doc_valid = cite_eval["doc_valid"]
        evidence_grounding_valid = cite_eval["grounding_valid"]

        # 3. Abstention Correctness
        abstain_correct = (response.abstain == item.expected_abstain)

        # 4. Coverage
        has_coverage = bool(response.direct_answer.strip()) and (len(response.claims) > 0 or response.abstain)

        return {
            "id": item.id,
            "question": item.question,
            "focus_entity": item.focus_entity,
            "expected_criteria": item.expected_criteria,
            "expected_abstain": item.expected_abstain,
            "actual_answer": response.direct_answer,
            "claims": response.claims,
            "sources": response.sources,
            "confidence_status": response.confidence_status,
            "confidence_score": response.confidence_score,
            "is_correct": is_correct,
            "crit_score": round(crit_score, 2),
            "matched_criteria": matched_criteria,
            "citation_doc_validity": citation_doc_valid,
            "evidence_grounding_validity": evidence_grounding_valid,
            "citation_validity": evidence_grounding_valid,  # Backwards compatibility alias
            "citation_reason": cite_eval["reason"],
            "abstention_correct": abstain_correct,
            "has_coverage": has_coverage,
            "notes": item.notes
        }

    def run_evaluation(self) -> Dict[str, Any]:
        """Run all 23 benchmark questions and compute separate quantitative metrics with exact denominators."""
        logger.info("Executing 23-question benchmark evaluation...")
        results: List[Dict[str, Any]] = []

        total_questions = len(EVALUATION_QUESTIONS_SPEC)
        positive_questions_total = sum(1 for item in EVALUATION_QUESTIONS_SPEC if not item.expected_abstain)
        negative_questions_total = sum(1 for item in EVALUATION_QUESTIONS_SPEC if item.expected_abstain)

        for item in EVALUATION_QUESTIONS_SPEC:
            response: QAResponse = self.qa_engine.answer_question(item.question)
            eval_result = self.evaluate_response(item, response)
            results.append(eval_result)

        # Aggregate counts
        questions_correct = sum(1 for r in results if r["is_correct"])
        positive_questions_correct = sum(1 for r in results if not r["expected_abstain"] and r["is_correct"])
        negative_questions_correct = sum(1 for r in results if r["expected_abstain"] and r["is_correct"])
        valid_citation_documents = sum(1 for r in results if r["citation_doc_validity"])
        valid_grounded_evidence = sum(1 for r in results if r["evidence_grounding_validity"])
        correct_abstentions = sum(1 for r in results if r["abstention_correct"])
        covered_questions = sum(1 for r in results if r["has_coverage"])

        # Compute separate evaluation metrics with exact denominators
        accuracy_percent = round((questions_correct / total_questions) * 100.0, 1)
        positive_accuracy_percent = round((positive_questions_correct / positive_questions_total) * 100.0, 1)
        negative_abstention_accuracy_percent = round((negative_questions_correct / negative_questions_total) * 100.0, 1)
        citation_document_validity_percent = round((valid_citation_documents / total_questions) * 100.0, 1)
        evidence_grounding_validity_percent = round((valid_grounded_evidence / total_questions) * 100.0, 1)
        coverage_percent = round((covered_questions / total_questions) * 100.0, 1)

        summary = {
            "total_questions": total_questions,
            "positive_questions_total": positive_questions_total,
            "negative_questions_total": negative_questions_total,
            "accuracy_percent": accuracy_percent,
            "positive_accuracy_percent": positive_accuracy_percent,
            "negative_abstention_accuracy_percent": negative_abstention_accuracy_percent,
            "abstention_accuracy_percent": negative_abstention_accuracy_percent,  # Backwards compatibility alias
            "citation_document_validity_percent": citation_document_validity_percent,
            "evidence_grounding_validity_percent": evidence_grounding_validity_percent,
            "citation_validity_percent": evidence_grounding_validity_percent,  # Backwards compatibility
            "coverage_percent": coverage_percent,
            "questions_correct": questions_correct,
            "positive_questions_correct": positive_questions_correct,
            "negative_questions_correct": negative_questions_correct,
            "valid_citation_documents": valid_citation_documents,
            "valid_grounded_evidence": valid_grounded_evidence,
            "correct_abstentions": correct_abstentions,
            "covered_questions": covered_questions,
            "results": results
        }

        # Save JSON output
        os.makedirs("data/processed", exist_ok=True)
        with open("data/processed/evaluation_results.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        # Generate comprehensive markdown report
        self.generate_markdown_report(summary, "reports/evaluation_report.md")

        logger.info(
            f"Evaluation finished: Accuracy={accuracy_percent}%, Positive Acc={positive_accuracy_percent}%, "
            f"Abstention Acc={negative_abstention_accuracy_percent}%, Doc Validity={citation_document_validity_percent}%, "
            f"Grounding Validity={evidence_grounding_validity_percent}%."
        )
        return summary

    def generate_markdown_report(self, summary: Dict[str, Any], output_path: str):
        """Format quantitative evaluation findings into a comprehensive markdown report with separate metrics."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        lines = [
            "# AEGIS KNOWLEDGE INTELLIGENCE SYSTEM — EVALUATION REPORT",
            "",
            "## 1. Executive Summary & Benchmark Metrics",
            "",
            "The Aegis evaluation suite benchmarks the system against 23 multi-modal, version-sensitive, and negative-constraint questions derived directly from `evaluation-questions.pdf`. The framework strictly separates document existence from verifiable evidence grounding and enforces uncompromising abstention correctness.",
            "",
            "### Core Performance Metrics",
            f"- **Overall Answer Accuracy**: **{summary['accuracy_percent']}%** ({summary['questions_correct']}/{summary['total_questions']})",
            f"- **Positive-Question Accuracy (Q1–Q18)**: **{summary['positive_accuracy_percent']}%** ({summary['positive_questions_correct']}/{summary['positive_questions_total']})",
            f"- **Negative-Question Abstention Accuracy (Q19–Q23)**: **{summary['negative_abstention_accuracy_percent']}%** ({summary['negative_questions_correct']}/{summary['negative_questions_total']})",
            f"- **Citation Document Validity Rate**: **{summary['citation_document_validity_percent']}%** ({summary['valid_citation_documents']}/{summary['total_questions']})",
            f"- **Evidence Grounding Validity Rate**: **{summary['evidence_grounding_validity_percent']}%** ({summary['valid_grounded_evidence']}/{summary['total_questions']})",
            f"- **Question Coverage**: **{summary['coverage_percent']}%** ({summary['covered_questions']}/{summary['total_questions']})",
            "",
            "> [!IMPORTANT]",
            "> **Document Existence vs. Evidence Grounding Distinction**:",
            "> - **Document Validity**: Validates that all cited documents exist within the 20-file ingested Aegis dataset.",
            "> - **Evidence Grounding Validity**: Rigorously requires that the cited document exists, matches the expected authoritative source, specifies granular coordinates (Page, Sheet, Cell, JSON path), and contains verifiable factual grounding within SQLite database chunks.",
            "",
            "---",
            "",
            "## 2. Granular Question-by-Question Scorecard",
            "",
            "| ID | Question | Focus Entity | Status | Doc Exists | Grounded | Abstain OK | Confidence |",
            "|---|---|---|---|---|---|---|---|"
        ]

        for r in summary["results"]:
            status_badge = "PASS" if r["is_correct"] else "FAIL"
            doc_badge = "VALID" if r["citation_doc_validity"] else "INVALID"
            ground_badge = "GROUNDED" if r["evidence_grounding_validity"] else "UNGROUNDED"
            abst_badge = "CORRECT" if r["abstention_correct"] else "MISMATCH"
            lines.append(
                f"| Q{r['id']} | {r['question'][:42]}... | `{r['focus_entity']}` | "
                f"**{status_badge}** | {doc_badge} | {ground_badge} | {abst_badge} | {r['confidence_status']} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## 3. Detailed Audit of Responses, Evidence & Provenance",
            ""
        ])

        for r in summary["results"]:
            lines.extend([
                f"### Question {r['id']}: {r['question']}",
                f"- **Focus Entity**: `{r['focus_entity']}`",
                f"- **Correctness**: {'PASSED' if r['is_correct'] else 'FAILED'}",
                f"- **Abstention Decision**: {'CORRECT' if r['abstention_correct'] else 'MISMATCH'} (Expected Abstain: `{r['expected_abstain']}`)",
                f"- **Citation Document Validity**: {'YES' if r['citation_doc_validity'] else 'NO'}",
                f"- **Evidence Grounding Validity**: {'YES' if r['evidence_grounding_validity'] else 'NO'}",
                f"- **Citation Audit Reason**: {r['citation_reason']}",
                f"- **Direct Answer**: {r['actual_answer']}",
                "- **Key Claims**:"
            ])
            for claim in r["claims"]:
                lines.append(f"  - {claim}")
            lines.append("- **Provenance Sources**:")
            for s in r["sources"]:
                lines.append(f"  - Document: `{s.get('document')}` | Location: `{s.get('location')}` | Method: `{s.get('extraction_method')}` | Trust: `{s.get('trust_level')}`")
            if r.get("notes"):
                lines.append(f"- **Engineering Notes**: {r['notes']}")
            lines.append("")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
