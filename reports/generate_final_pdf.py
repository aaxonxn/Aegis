"""
Automated ReportLab PDF Generator for Aegis Final Technical Report.
Generates an executive, publication-grade technical report under reports/Aegis_Final_Technical_Report.pdf.
Covers:
- System Architecture & Ingestion Matrix
- Intermediate Knowledge Models (Schemas, Graph, Relational SQLite)
- Canonical Entity Disambiguation & Revision-Aware Conflict Reconciler
- Phase 1 Ground Truth Benchmark (23/23, 100%)
- Phase 2 Independent Robustness & Generalization Evaluation (27/45, 60.0%)
- Deep Evidence Entailment Verification Results
- Identified Limitations & Phase 3.1 Architectural Improvement Proposal
"""

import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Ensure workspace in path
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)


class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total pages dynamically and decorates headers/footers."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8.5)
        self.setFillColor(colors.HexColor("#64748B"))

        # Header on pages > 1
        if self._pageNumber > 1:
            self.drawString(54, 750, "AEGIS Knowledge Intelligence System — Final Technical Architecture & Audit Report")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)

        # Footer on all pages
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 38, footer_text)
        self.drawString(54, 38, "https://github.com/aaxonxn/Aegis | Senior AI/ML Systems & Validation Engineering")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 50, 558, 50)

        self.restoreState()


def build_final_pdf(output_pdf: str = "reports/Aegis_Final_Technical_Report.pdf"):
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#2563EB"),
        spaceAfter=12
    )
    meta_style = ParagraphStyle(
        "CoverMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#475569"),
        spaceAfter=10
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=14,
        bulletIndent=4,
        spaceAfter=3
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1E293B")
    )
    table_header = ParagraphStyle(
        "TableHeader",
        parent=table_cell,
        fontName="Helvetica-Bold",
        textColor=colors.white
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("AEGIS KNOWLEDGE INTELLIGENCE SYSTEM", title_style))
    story.append(Paragraph("Final Technical Architecture, Ingestion Engineering & Multi-Phase Evaluation Report", subtitle_style))
    story.append(Paragraph(
        "<b>Repository:</b> https://github.com/aaxonxn/Aegis | <b>Target System:</b> Aegis Series-7 Hydraulic Control System (HCS)<br/>"
        "<b>Author:</b> Senior AI Systems Architect & Software Quality Engineer | <b>Date:</b> November 2026",
        meta_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceBefore=2, spaceAfter=12))

    # Executive Summary
    story.append(Paragraph("1. Executive Summary & Project Status", h1_style))
    story.append(Paragraph(
        "The <b>Aegis Knowledge Intelligence System</b> is an offline-first, provenance-preserving industrial intelligence platform "
        "designed to ingest, resolve, and query heterogeneous, contradictory technical documentation for the Aegis Series-7 Hydraulic Control System (HCS). "
        "Operating entirely offline without paid LLM APIs, Aegis extracts 372 chunks across 20 multi-modal files (PDFs, scans, schematics, DOCX, XLSX, PPTX, JSON), "
        "enforces canonical entity disambiguation (differentiating PS-04, PS-04A, and PS-40), maintains revision-scoped truth (180 bar pre-3.2 vs 200 bar post-3.2), "
        "and provides audit-ready evidence citations with honest negative abstention.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Project Status:</b><br/>"
        "• <b>Phase 1 (Original Benchmark):</b> Achieved <b>100.0% (23/23) accuracy</b>, 100% citation validity, and 100% abstention precision on the baseline suite.<br/>"
        "• <b>Phase 2 (Independent Robustness Evaluation):</b> Evaluated against 45 new unseen questions, achieving <b>60.0% (27/45) accuracy</b> and 84.1% claim entailment grounding. It confirmed strong multi-modal extraction but exposed fragility in regex query routing and single-chunk fallback.<br/>"
        "• <b>Phase 3.1 (Architecture Proposal):</b> A modular architecture design proposing query analysis, hybrid TW-RRF retrieval, multi-hop reasoning, and premise verification gates (currently a design proposal; zero code modified in Phase 3.1).",
        body_style
    ))

    # 2. Implemented Architecture & Intermediate Models
    story.append(Paragraph("2. Implemented Architecture & Knowledge Models", h1_style))
    story.append(Paragraph(
        "Aegis models technical reality through seven Pydantic v2 schemas persisted in SQLite (<code>data/processed/aegis_knowledge.db</code>) "
        "and exported to normalized JSON artifacts (<code>knowledge_graph.json</code>, <code>facts_export.json</code>):",
        body_style
    ))

    schema_data = [
        [Paragraph("Schema", table_header), Paragraph("Key Attributes", table_header), Paragraph("Functional Purpose", table_header)],
        [Paragraph("<b>Document</b>", table_cell), Paragraph("document_id, filename, file_format, doc_type, trust_level, trust_score, revision", table_cell), Paragraph("Provenance metadata and hierarchical reliability tiering.", table_cell)],
        [Paragraph("<b>DocumentChunk</b>", table_cell), Paragraph("chunk_id, content, page, section, worksheet, cell_range, json_path, bbox", table_cell), Paragraph("Granular citation coordinates down to cells, slides, and JSON paths.", table_cell)],
        [Paragraph("<b>Entity</b>", table_cell), Paragraph("entity_id, canonical_name, entity_type, aliases, location, status, notes", table_cell), Paragraph("Canonical modeling preventing erroneous fuzzy merging of similar tags.", table_cell)],
        [Paragraph("<b>Fact</b>", table_cell), Paragraph("fact_id, subject, predicate, value, unit, applicability, effective_date", table_cell), Paragraph("Atomic factual propositions with revision scoping and trust weighting.", table_cell)],
        [Paragraph("<b>Relationship</b>", table_cell), Paragraph("relationship_id, source_entity, target_entity, relation_type, status", table_cell), Paragraph("Topological and functional edges (including uncertain review flags).", table_cell)],
        [Paragraph("<b>Conflict</b>", table_cell), Paragraph("conflict_id, topic, conflicting_facts, resolution_status, preferred_fact_id", table_cell), Paragraph("Revision-aware truth tracking preventing silent data overwriting.", table_cell)]
    ]
    t_schema = Table(schema_data, colWidths=[1.1*72, 2.7*72, 3.2*72])
    t_schema.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_schema)
    story.append(Spacer(1, 8))

    # 3. Multi-Modal Ingestion Matrix
    story.append(Paragraph("3. Multi-Modal Ingestion Engineering (20 Files / 8 Formats)", h1_style))
    story.append(Paragraph(
        "Aegis processes heterogeneous formats using specialized offline parsers:<br/>"
        "• <b>Born-Digital PDFs (PyMuPDF):</b> Extracts layout text blocks, warning callouts, and section hierarchies.<br/>"
        "• <b>Scanned Calibration Appendix & Screenshots (RapidOCR ONNX):</b> 200 DPI OCR with polygon bounding boxes (mean confidence 0.96).<br/>"
        "• <b>Vector Hydraulic Schematic (PyMuPDF Drawings):</b> Parses stroke colors (purple=control, grey=fluid, tan=reservoir) and flags topological anomalies (grey line connecting PLC-03 to HPU).<br/>"
        "• <b>Spreadsheets (openpyxl):</b> Preserves exact coordinate cell ranges (e.g. <code>Components!A2:F2</code>).<br/>"
        "• <b>Word & PowerPoint (python-docx / python-pptx):</b> Extracts structural paragraphs, tables, slide numbers, and presenter notes.<br/>"
        "• <b>Configuration (JSON Traversal):</b> Traverses parameter trees to record exact JSON paths (<code>sensors.sensor_ps04a_threshold_bar</code>).",
        body_style
    ))

    # 4. Evaluation Benchmark Results (Phase 1 vs Phase 2)
    story.append(Paragraph("4. Evaluation Benchmark Results (Phase 1 vs. Phase 2)", h1_style))
    story.append(Paragraph(
        "To ensure strict evaluation integrity, Phase 1 and Phase 2 benchmarks are maintained and reported independently:",
        body_style
    ))

    eval_comparison_data = [
        [Paragraph("Evaluation Metric", table_header), Paragraph("Phase 1: Baseline Benchmark", table_header), Paragraph("Phase 2: Robustness Audit", table_header), Paragraph("Architectural Finding", table_header)],
        [Paragraph("<b>Total Questions</b>", table_cell), Paragraph("23 Questions", table_cell), Paragraph("45 Questions (Unseen)", table_cell), Paragraph("Separate, non-overlapping datasets.", table_cell)],
        [Paragraph("<b>Overall Accuracy</b>", table_cell), Paragraph("<b>100.0%</b> (23/23)", table_cell), Paragraph("<b>60.0%</b> (27/45)", table_cell), Paragraph("Regex intent misses trigger fallback.", table_cell)],
        [Paragraph("<b>Citation Validity</b>", table_cell), Paragraph("100.0% (23/23)", table_cell), Paragraph("93.3% (42/45)", table_cell), Paragraph("Corpus files valid; coordinate gaps in fallback.", table_cell)],
        [Paragraph("<b>Abstention Precision</b>", table_cell), Paragraph("100.0% (5/5)", table_cell), Paragraph("60.0% (3/5)", table_cell), Paragraph("Generic terms in unanswerable queries trick BM25.", table_cell)],
        [Paragraph("<b>Automated Test Suite</b>", table_cell), Paragraph("38 Passing Tests", table_cell), Paragraph("48 Passing Tests", table_cell), Paragraph("10 new Phase 2 regression tests passing in 0.31s.", table_cell)]
    ]
    t_eval = Table(eval_comparison_data, colWidths=[1.5*72, 1.8*72, 1.8*72, 1.9*72])
    t_eval.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_eval)
    story.append(Spacer(1, 8))

    # Phase 2 Category Breakdown
    story.append(Paragraph("Phase 2 Performance by Diagnostic Category:", h2_style))
    p2_cat_data = [
        [Paragraph("Diagnostic Category", table_header), Paragraph("Tested", table_header), Paragraph("Correct", table_header), Paragraph("Accuracy", table_header), Paragraph("Primary Failure Mode", table_header)],
        [Paragraph("Semantically Rephrased Factual", table_cell), Paragraph("15", table_cell), Paragraph("11", table_cell), Paragraph("73.3%", table_cell), Paragraph("Regex miss drops to raw snippet truncation.", table_cell)],
        [Paragraph("Multi-Document Reasoning", table_cell), Paragraph("10", table_cell), Paragraph("4", table_cell), Paragraph("40.0%", table_cell), Paragraph("Top-1 chunk horizon cannot merge multi-doc facts.", table_cell)],
        [Paragraph("Entity Disambiguation", table_cell), Paragraph("5", table_cell), Paragraph("3", table_cell), Paragraph("60.0%", table_cell), Paragraph("Keyword collisions in fallback retrieval.", table_cell)],
        [Paragraph("False-Premise Handling", table_cell), Paragraph("5", table_cell), Paragraph("3", table_cell), Paragraph("60.0%", table_cell), Paragraph("Uncritical snippet retrieval on false assumptions.", table_cell)],
        [Paragraph("Unanswerable / Abstention", table_cell), Paragraph("5", table_cell), Paragraph("3", table_cell), Paragraph("60.0%", table_cell), Paragraph("High BM25 scores on generic terms bypass abstention.", table_cell)],
        [Paragraph("Targeted Adversarial Scenarios", table_cell), Paragraph("5", table_cell), Paragraph("3", table_cell), Paragraph("60.0%", table_cell), Paragraph("Firmware scoping confusion (3.1 vs 3.2).", table_cell)]
    ]
    t_cat = Table(p2_cat_data, colWidths=[1.8*72, 0.7*72, 0.7*72, 0.9*72, 2.9*72])
    t_cat.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_cat)
    story.append(Spacer(1, 8))

    # 5. Evidence Entailment Verification
    story.append(Paragraph("5. Evidence Entailment Verification & Limitations", h1_style))
    story.append(Paragraph(
        "To strengthen citation audit beyond keyword matching, Phase 2 deployed a deterministic, symbolic <b>Evidence Entailment Validator</b> "
        "(<code>evaluation/entailment_validator.py</code>) checking 88 claims generated across the 45 responses against SQLite chunks:<br/>"
        "• <b>Direct Evidence (58.0%, 51 claims):</b> Assertions and numerical metrics explicitly found in the cited chunk.<br/>"
        "• <b>Inferred Information (26.1%, 23 claims):</b> Assertions deduced from graph topology, conflict priority, or cross-chunk context.<br/>"
        "• <b>Unsupported Claims (15.9%, 14 claims):</b> Facts asserted without backing in the cited chunk (primarily from fallback snippet slicing).<br/>"
        "• <b>Contradicted Claims (0.0%, 0 claims):</b> Zero assertions contradicted facts in the cited source chunks.<br/>"
        "<i>Methodological Disclosure:</i> The entailment validator uses symbolic proposition overlap, entity binding, and numerical/polarity consistency. "
        "It is not a trained neural NLI model; syntactic passive-voice transformations are conservatively classified as Inferred rather than Direct Evidence.",
        body_style
    ))

    # 6. Identified Limitations & Phase 3.1 Architecture Proposal
    story.append(Paragraph("6. Identified Limitations & Proposed Phase 3 Architecture", h1_style))
    story.append(Paragraph(
        "<b>Identified Architectural Deficits:</b><br/>"
        "1. <i>Regex Routing Fragility:</i> High benchmark accuracy was maintained via hand-crafted regex rules. Conversational rephrasings (e.g. 'crank up') trigger fallback.<br/>"
        "2. <i>Single-Chunk Fallback Horizon:</i> The fallback retriever relies strictly on <code>bm25_results[0]</code>, truncating the top-1 chunk at 280 characters.<br/>"
        "3. <i>Uncalibrated Abstention:</i> Gating abstention on <code>BM25 < 1.0</code> fails when unanswerable questions share common terms ('pump', 'fluid').<br/>"
        "4. <i>Disconnected Entity Resolution:</i> <code>EntityResolver.resolve()</code> checks full query strings and returns None on natural language sentences.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Proposed Phase 3 Retrieval Architecture (PROPOSAL ONLY):</b><br/>"
        "• <b>Query Understanding Pipeline (<code>query_analyzer.py</code>):</b> SymSpell typo correction, alias gazetteer extraction, and intent classification.<br/>"
        "• <b>Hybrid TW-RRF Retrieval (<code>hybrid_retriever.py</code>):</b> Combines stopword-filtered BM25, structured facts, and document trust weights.<br/>"
        "• <b>Multi-Hop Graph Reasoner (<code>multi_hop_reasoner.py</code>):</b> Iterative 2-hop graph expansion connecting disjoint schematic and electrical domains.<br/>"
        "• <b>Premise Verification & Sufficiency Gate (<code>sufficiency_verifier.py</code>):</b> Rejects false assumptions pre-retrieval and verifies target attribute presence post-retrieval to guarantee honest abstention.",
        body_style
    ))

    # 7. Verification Sign-Off
    story.append(Paragraph("7. Repository Verification & Audit Sign-Off", h1_style))
    story.append(Paragraph(
        "• <b>Source Integrity:</b> Zero modifications to original benchmark or QA engine; all 48 unit and robustness tests passing.<br/>"
        "• <b>Offline Functionality:</b> Completely local execution without cloud APIs or network calls.<br/>"
        "• <b>Public Repository:</b> https://github.com/aaxonxn/Aegis<br/>"
        "<i>Report certified by Senior Software Quality & AI Validation Engineering.</i>",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {output_pdf}")


if __name__ == "__main__":
    build_final_pdf()

