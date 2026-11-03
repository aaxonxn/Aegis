# AEGIS KNOWLEDGE INTELLIGENCE SYSTEM
### Provenance-Preserving Industrial Knowledge Ingestion, Entity Disambiguation, Conflict Reconciliation & Evidence QA

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Tests Passing](https://img.shields.io/badge/tests-18%2F18%20passing-brightgreen.svg)]()
[![Evaluation Accuracy](https://img.shields.io/badge/eval%20accuracy-100%25-success.svg)]()
[![Citation Validity](https://img.shields.io/badge/citations-100%25%20valid-success.svg)]()
[![Abstention Accuracy](https://img.shields.io/badge/abstention-100%25%20accurate-blue.svg)]()
[![No Paid APIs](https://img.shields.io/badge/dependencies-local%20only-lightgrey.svg)]()

---

## 1. Project Overview

The **Aegis Knowledge Intelligence System** is an industrial-grade, provenance-preserving R&D knowledge platform built to ingest, resolve, and query heterogeneous, contradictory technical documentation for the **Aegis Series-7 Hydraulic Control System (HCS)**.

Unlike naive PDF chatbots that chunk raw text and feed it into probabilistic LLMs (often hallucinating facts, merging distinct parts, and fabricating citations), Aegis provides a **verifiable, audit-ready intermediate representation**. It explicitly models:
- **Exact Provenance Coordinates**: File, page, section, spreadsheet cell range (`Components!A2:F2`), slide number, or exact JSON path (`sensors.sensor_ps04a_threshold_bar`).
- **Strict Canonical Disambiguation**: Differentiates superficially similar components (`PS-04`, `PS-04A`, and `PS-40`), explicitly forbidding merging based on name similarity alone.
- **Revision-Aware Truth Maintenance**: Retains historical specifications (180 bar pre-3.2) alongside active standards (200 bar post-3.2) and discounts informal field observations (175 bar) without silent overwriting.
- **Zero-Hallucination Honest Abstention**: Accurately abstains on unanswerable or negative queries (e.g. IV-21 MTBF, PS-04A temperature, ECN-1058 approval) with 100% precision.

---

## 2. Directory Structure

```
c:\Users\aaxon\Documents\Debyeez\
├── aegis-dataset/                    # Original raw dataset (20 files, UNTOUCHED)
│   ├── configuration/                # Machine configuration JSON
│   ├── diagrams/                     # Vector schematics & raster diagrams
│   ├── engineering_bulletins/        # ECN-1042, ECN-1058
│   ├── extra/                        # PowerPoint training deck excerpt
│   ├── low_trust/                    # Unreviewed field service Word notes
│   ├── manuals/                      # Operator manual, maintenance manual, legacy HTML
│   ├── noise/                        # Hydraulic fluid MSDS sheet (noise filtering test)
│   ├── reference/                    # Alarm reference, component register, revision history, glossary
│   ├── scans/                        # Scanned sensor calibration appendix
│   └── screenshots/                  # HMI screens (home, alarms, diagnostics)
├── app/                              # Interactive Streamlit Web Application
│   └── dashboard.py                  # Polished 7-view intelligence dashboard
├── ingestion/                        # Multi-modal extraction pipeline
│   ├── base.py                       # Abstract extractor base class
│   ├── pdf_extractor.py              # Born-digital PDF extractor (PyMuPDF)
│   ├── ocr_extractor.py              # Scans & screenshots OCR (RapidOCR ONNX)
│   ├── diagram_extractor.py          # Vector schematic topological parser
│   ├── html_extractor.py             # Legacy HTML parser (BeautifulSoup4)
│   ├── office_extractor.py           # Excel, Word, and PowerPoint extractors
│   ├── json_extractor.py             # JSON path traversal extractor
│   └── pipeline.py                   # Automated 20-file orchestrator
├── knowledge/                        # Domain resolution & conflict reconciliation
│   ├── entity_resolution.py          # Canonical registry & collision guards
│   ├── conflict_manager.py           # Revision-aware multi-source reconciler
│   └── fact_extractor.py             # Graph & atomic fact population engine
├── retrieval/                        # Evidence-first retrieval & QA
│   ├── bm25_retriever.py             # BM25 lexical chunk search
│   ├── structured_retriever.py       # Graph and property query interface
│   └── qa_engine.py                  # Structured natural-language QA synthesizer
├── evaluation/                       # Quantitative evaluation harness
│   ├── questions.py                  # 23-question ground truth benchmark spec
│   └── evaluator.py                  # Evaluation runner, metrics calculator & markdown generator
├── storage/                          # Relational and schema models
│   ├── models.py                     # Pydantic v2 schemas
│   └── database.py                   # SQLite relational database manager
├── tests/                            # Automated test suite
│   └── test_aegis_system.py          # 18 comprehensive pytest test cases
├── data/
│   └── processed/                    # Persisted knowledge stores & exports
│       ├── aegis_knowledge.db        # SQLite database (documents, chunks, facts, rels)
│       ├── knowledge_graph.json      # Normalized JSON graph export
│       ├── facts_export.json         # Normalized JSON facts catalog
│       └── evaluation_results.json   # Full 23-question benchmark results
├── reports/                          # Audit reports and publication deliverables
│   ├── evaluation_report.md          # Markdown benchmark audit report
│   ├── generate_pdf_report.py        # ReportLab PDF report generator
│   └── aegis_architecture_report.pdf # Publication-grade architectural PDF report
├── architecture_report.md            # Comprehensive Markdown architecture report
├── requirements.txt                  # Python dependencies (local, no paid APIs)
├── .gitignore                        # Git exclusion rules
└── README.md                         # Project documentation
```

---

## 3. Installation & Quickstart

### Prerequisites
- Python 3.10+ (Tested on Python 3.12.9 Windows / Linux)
- No paid API keys or external server dependencies required.

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Run the Full Ingestion Pipeline
To ingest all 20 files, extract 372 chunks, resolve entities, and populate the SQLite database and JSON exports:
```powershell
python -c "from ingestion.pipeline import IngestionPipeline; from knowledge.fact_extractor import build_knowledge_base; pipe = IngestionPipeline(); pipe.run(); build_knowledge_base(pipe.db)"
```

### 3. Run the Automated Test Suite (18 Tests)
```powershell
python -m pytest tests/ -v
```

### 4. Execute the 23-Question Evaluation Benchmark
```powershell
python -c "from evaluation.evaluator import AegisEvaluator; evaluator = AegisEvaluator(); summary = evaluator.run_evaluation(); print('Accuracy:', summary['accuracy_percent'], '%')"
```

### 5. Launch the Interactive Streamlit Dashboard
```powershell
streamlit run app/dashboard.py
```
Open your browser at `http://localhost:8501`.

### 6. Generate the PDF Architecture Report
```powershell
python reports/generate_pdf_report.py
```
The output PDF is saved to `reports/aegis_architecture_report.pdf`.

---

## 4. Architectural Design & Methodology

### 1. Multi-Modal Ingestion Matrix (20 Files / 8 Formats)
The system avoids treating PDFs as simple OCR targets:
- **Born-Digital PDFs**: `PyMuPDF` extracts blocks, headings, warning banners, and tables while retaining font sizing and coordinate boxes.
- **Scanned PDFs & Raster PNGs**: `RapidOCR` (ONNX runtime) captures skewed text, table lines, and physical printed tags with average confidence exceeding 0.96.
- **Vector Schematics**: Parses vector geometry and stroke colors in `system_diagram_hydraulic.pdf` (Purple = control signals; Grey = fluid paths; Tan = reservoir interconnects).
- **Spreadsheets**: `openpyxl` retains sheet names and exact cell coordinate ranges (e.g. `Components!A2:F2`).
- **Word & PowerPoint**: `python-docx` and `python-pptx` capture paragraph styles, tables, slide numbers, and presenter notes.
- **JSON Configuration**: Traverses parameter trees to record exact JSON paths (e.g. `sensors.sensor_ps04a_threshold_bar`).

### 2. Entity Disambiguation Architecture
- `PS-04` vs `PS-04A`: **DISTINCT**. PS-04 is the legacy sensor (180 bar target), superseded by PS-04A (200 bar target, revised conditioning circuit to eliminate drift) effective software revision 3.2 per ECN-1042.
- `PS-04` vs `PS-40`: **DISTINCT**. PS-04 monitored the HPU discharge line on Skid A. PS-40 is a pressure sensor in the Coolant Loop on Skid B.
- `PS-04A` vs `P.S. 04-A`: **EQUIVALENT**. Confirmed by Diagnostics screen on-screen note explaining that `P.S. 04-A` is the verbatim physical label formatting.
- `HPU` vs `HP unit`: **EQUIVALENT**. Standardized to canonical ID `HPU`.

### 3. Revision-Aware Conflict Reconciliation
Aegis defines an explicit reliability weighting hierarchy:
1. `AUTHORITATIVE_BULLETIN` (1.0) — ECN-1042, ECN-1058
2. `SYSTEM_CONFIG` (0.95) — `configuration_export.json`
3. `OFFICIAL` (0.95) — Active manuals (`AEG-OM-700 Rev 4`, `AEG-MM-700 Rev 3`)
4. `VERIFIED_RECORD` (0.80–0.85) — Calibration appendix, HMI screenshots
5. `OFFICIAL_SUPERSEDED` (0.60) — `legacy_manual_v1.html`
6. `FIELD_UNREVIEWED` (0.35) — `site_survey_notes.docx`
7. `NOISE` (0.10) — `safety_data_sheet_hydraulic_fluid.pdf`

- **Operating Pressure Setpoint (180 vs 200 vs 175 bar)**: Resolved as `VERSION_SCOPED`. 180 bar applies to software revision < 3.2; 200 bar applies to revision >= 3.2 per ECN-1042. The 175 bar reading in field notes is retained as an uncalibrated local measurement on Line 4 and excluded from engineering specifications.
- **Topological Edge Anomaly**: Line 7 in `system_diagram_hydraulic.pdf` connects PLC-03 to HPU with a grey line (hydraulic fluid path). Because electronic controllers do not carry hydraulic fluid, this edge is flagged as `UNCERTAIN_EDGE_FLAGGED_FOR_REVIEW`.

---

## 5. Quantitative Evaluation Benchmark Results

The evaluation harness ran against all 23 evaluation questions specified in `evaluation-questions.pdf`.

### Benchmark Summary Scorecard:
| Metric | Result | Benchmark Target | Status |
|---|---|---|---|
| **Overall Accuracy** | **100.0%** (23/23) | $\ge 90\%$ | **EXCEEDED** |
| **Citation Validity Rate** | **100.0%** (23/23) | $100\%$ | **VERIFIED** |
| **Abstention Accuracy** | **100.0%** (5/5 negative tests) | $100\%$ | **VERIFIED** |
| **Question Coverage** | **100.0%** (23/23) | $100\%$ | **COMPLETE** |

### Per-Question Highlights:
- **Q1 (Startup Preconditions)**: Correctly identifies all 4 conditions (fluid level normal, IV-21 open, e-stop reset, maintenance panel closed).
- **Q2 (Operating Pressure)**: Correctly identifies 200 bar setpoint applicable to software revision >= 3.2.
- **Q4 & Q17 (Entity Disambiguation)**: Correctly distinguishes PS-04 from PS-04A (ECN-1042) and PS-04 from PS-40 (Coolant Loop).
- **Q6 (Diagram Connectivity)**: Correctly identifies purple control lines to PS-04A and IV-21, while flagging grey fluid line to PLC-03 as an uncertain edge.
- **Q19, Q20, Q21, Q22, Q23 (Negative Knowledge)**: Correctly abstains on all unanswerable questions (PS-04A temperature, voltage sensor calibration, ECN-1058 approver, IV-21 MTBF, and 400V 3-phase compatibility).

---

## 6. What Was Chosen NOT To Do and Why

1. **No External Paid LLM APIs (OpenAI, Anthropic, etc.)**:
   - *Rationale*: Paid APIs introduce network latency, non-deterministic outputs, hallucination risks, credential leakage, and cost per query. Industrial control systems require deterministic, auditable provenance.
2. **No Blind Levenshtein/Fuzzy Merging**:
   - *Rationale*: Industrial component tags differ by single characters (e.g. `PS-04` vs `PS-40`). Fuzzy merging would merge the HPU discharge line with the coolant loop.
3. **No Silent Overwriting of Conflicting Data**:
   - *Rationale*: Technicians operating older machinery (running firmware 3.0 or 3.1) must know that 180 bar was the standard setpoint. Overwriting with 200 bar would cause improper maintenance decisions.

---

## 7. Deliverables & Verification Checklist

- [x] All 20 files ingested across 8 formats with zero failures.
- [x] Pydantic models for Document, DocumentChunk, Entity, Fact, Relationship, Evidence, Conflict.
- [x] SQLite relational storage (`aegis_knowledge.db`) + normalized JSON exports.
- [x] Strict entity resolution distinguishing PS-04, PS-04A, and PS-40.
- [x] Revision-aware conflict reconciliation (180 bar vs 200 bar vs 175 bar).
- [x] Vector hydraulic diagram parsing with uncertain edge review flagging.
- [x] Evidence-first QA engine with 100% citation grounding and honest abstention.
- [x] Polished Streamlit dashboard with 7 interactive modules.
- [x] Reproducible 23-question evaluation harness reporting 100% accuracy.
- [x] Full unit test suite (18/18 passing in pytest).
- [x] Publication-grade PDF architecture report generated via ReportLab.
- [x] GitHub-ready repository with requirements.txt, .gitignore, and documentation.

