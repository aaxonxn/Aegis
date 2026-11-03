# AEGIS SYSTEM VALIDATION AUDIT – PHASE 2: INDEPENDENT ROBUSTNESS & GENERALIZATION REPORT

**Validation Role:** Senior AI Systems Validation Engineer  
**Audit Target:** Aegis Knowledge Intelligence System (Series-7 HCS R&D Corpus)  
**Evaluation Date:** November 3, 2026  
**Evaluation Scope:** 45 New, Unseen Questions Across 6 Diagnostic Categories  
**Corpus Constraints:** Offline Operation, Local SQLite/BM25/Graph, Zero Hardcoded Test Overfitting  
**Status:** Independent Audit Completed & Verified  

---

## Executive Summary

During Phase 1 evaluation, the Aegis Knowledge Intelligence System reported **100.0% accuracy (23/23)**, **100.0% citation validity**, and **100.0% abstention accuracy** against its original benchmark suite. 

To establish whether Aegis genuinely possesses generalizable comprehension and evidence retrieval across heterogeneous industrial documentation—or whether Phase 1 results were heavily subsidized by question-specific regex intent routes—we executed an unsparing, independent **Phase 2 Robustness, Semantic Generalization, and Adversarial Audit** using **45 newly constructed, unseen questions**.

### Key Findings at a Glance:
1. **Unseen Question Generalization Drop**: Overall accuracy dropped from **100.0% on the 23-question benchmark** to **60.0% (27/45)** on unseen queries.
2. **Brittle Routing vs. Naive Snippet Fallback**: Questions that matched the 23 hardcoded regex intents passed reliably; however, queries with slight terminology shifts, grammatical noise, or indirect phrasing fell through to the BM25 fallback, which merely returns raw truncated chunk text (`content[:280]`) rather than synthesized technical answers.
3. **Multi-Document Reasoning Bottleneck**: Multi-document reasoning accuracy collapsed to **40.0% (4/10)** because the fallback retrieval pipeline operates on a single top-1 chunk horizon (`top_chunk = bm25_results[0]`), rendering multi-source cross-referencing architecturally impossible outside pre-wired routes.
4. **False Premise Vulnerability**: When presented with false premises (e.g., asserting PS-40 is on the HPU discharge line or that PLC-03 can be reset at 100 bar), the system achieved **60.0% (3/5)**. It successfully rejected false premises only when queries intersected pre-existing guards; otherwise, it uncritically regurgitated chunks matching superficial keywords.
5. **Negative Knowledge Generalization Deficit**: While the 5 original negative benchmark questions abstained with 100% accuracy, unseen unanswerable questions (e.g., pump motor acoustic noise dBA, hydraulic fluid viscosity at 120°C) achieved only **60.0% (3/5)** abstention. BM25 matched generic tokens (`pump`, `fluid`), yielding a retrieval score $> 1.0$, which tricked the fallback engine into asserting answers with `HIGH` confidence.
6. **Evidence Entailment Grounding**: Deep evidence entailment validation (evaluated claim-by-claim against raw SQLite chunks) revealed that **58.0% (51/88)** of generated claims constitute direct verbatim evidence, **26.1% (23/88)** are inferred propositions, and **15.9% (14/88)** are unsupported by the cited source chunk. Contradictions remained at **0.0%**, demonstrating that when Aegis cites a verified chunk, it rarely fabricates contradictory facts.

---

## 1. Quantitative Scorecard: Benchmark Comparison

To ensure audit integrity, the original 23-question benchmark and the 45-question Phase 2 robustness suite are maintained strictly separately.

| Evaluation Suite | Total Questions | Passing / Correct | Accuracy Rate | Citation Validity | Abstention Precision | Entailment Grounding |
|---|---|---|---|---|---|---|
| **Phase 1 Benchmark (Original)** | 23 | 23 | **100.0%** | 100.0% | 100.0% (5/5) | Keyword Overlap Only |
| **Phase 2 Robustness (Unseen)** | 45 | 27 | **60.0%** | 93.3% | 60.0% (3/5) | **84.1%** (Deep Entailment) |

### Phase 2 Accuracy Breakdown by Category (Exact Denominators)

| Category | Total Questions | Correct Answers | Accuracy (%) | Primary Failure Mode |
|---|---|---|---|---|
| **1. Semantically Rephrased Factual** | 15 | 11 | **73.3%** | Regex intent miss $\rightarrow$ Fallback snippet truncation |
| **2. Multi-Document Reasoning** | 10 | 4 | **40.0%** | Single top-1 chunk horizon unable to synthesize cross-doc facts |
| **3. Entity Disambiguation** | 5 | 3 | **60.0%** | Keyword collision in unstructured chunks |
| **4. False-Premise Detection** | 5 | 3 | **60.0%** | Uncritical retrieval on false assumptions |
| **5. Unanswerable / Abstention** | 5 | 3 | **60.0%** | High BM25 scores on generic tokens suppress abstention |
| **6. Targeted Adversarial Scenarios** | 5 | 3 | **60.0%** | Cross-firmware scoping confusion |
| **OVERALL TOTAL** | **45** | **27** | **60.0%** | **18 Isolated Failures Documented** |

### Phase 2 Accuracy Breakdown by Variation Type

| Variation Mechanism | Count | Correct | Accuracy (%) | System Behavior & Observations |
|---|---|---|---|---|
| **Indirect Phrasing** | 3 | 3 | **100.0%** | Handled well when core technical entity keywords remained intact |
| **Abbreviations** | 2 | 2 | **100.0%** | Aliases (`PS04`, `10s`, `ECN-1042`) correctly normalized by tokenizers |
| **Conversational Tone** | 6 | 5 | **83.3%** | High pass rate, except when domain verbs were replaced (`crank up`) |
| **Adversarial Scoping** | 5 | 3 | **60.0%** | Struggled when firmware 3.1 was applied to 200 bar components |
| **False Assumptions** | 5 | 3 | **60.0%** | Accepted premises when question terms matched chunk text |
| **Terminology Shifts** | 11 | 6 | **54.5%** | Vulnerable when standard terms (`HPU`) were replaced |
| **Combined Facts** | 2 | 1 | **50.0%** | Partial coverage; captured one clause while omitting second |
| **Cross-Document Synthesis** | 10 | 4 | **40.0%** | Critical bottleneck: retriever cannot merge disjoint documents |
| **Misspellings / Typos** | 1 | 0 | **0.0%** | Exact BM25 tokenization failed completely on `wat`, `presure` |

---

## 2. Evidence Entailment Validation Results

Phase 1 evaluated citation validity using superficial document existence and keyword matching (`entity_present or matches_q >= 1`). In Phase 2, we introduced a rigorous **Evidence Entailment Validator** that inspects each individual claim against the actual text of the retrieved SQLite chunk.

### Claim Grounding Distribution (88 Total Claims Evaluated)

| Entailment Classification | Claim Count | Percentage | Validation Definition |
|---|---|---|---|
| **Direct Evidence** | 51 | **58.0%** | Proposition, entities, and numerical parameters are explicitly stated in the cited chunk text. |
| **Inferred Information** | 23 | **26.1%** | Proposition is logically deduced from cross-chunk context, graph relationships, or revision scoping rules. |
| **Unsupported Claims** | 14 | **15.9%** | Claim asserts details, dates, or parameters absent from or unprovable by the cited chunk. |
| **Contradicted Claims** | 0 | **0.0%** | Claim makes an assertion directly contrary to facts stated in the cited chunk. |

```
Entailment Distribution:
[█████████████████████████████                     ] 58.0% Direct Evidence
[█████████████                                     ] 26.1% Inferred Information
[████████                                          ] 15.9% Unsupported Claims
[                                                  ]  0.0% Contradicted Claims
```

### Citation Integrity Findings:
- **Zero Hallucinated Citations**: The system never fabricated a non-existent document or cited outside the 20-file corpus.
- **Granular Coordinate Preservation**: In 82.2% of citations, exact coordinates (Page numbers, Sheet names, JSON paths) were preserved.
- **Unsupported Claim Root Cause**: Unsupported claims occurred primarily during BM25 fallback, where the engine asserted structured claims from `get_entity_facts()` but cited only the top BM25 chunk, which did not contain those facts.

### Local Entailment Verification Methodology & Limitations
> [!NOTE]
> **Honest Engineering Disclosure on Local Validation:**
> The Phase 2 Evidence Entailment Validator operates completely locally without external cloud APIs. It performs deterministic symbolic verification: canonical entity binding, numerical consistency extraction (detecting conflicting bar/voltage/date values), polarity/negation alignment, and proposition token overlap.
> **Known Limitation:** Without a multi-billion-parameter neural Natural Language Inference (NLI) model (e.g., DeBERTa-v3-large-MNLI), complex syntactic passive-voice transformations and subtle semantic equivalences are classified as `INFERRED` rather than `DIRECT_EVIDENCE`. This provides conservative lower-bound estimates of direct entailment.

---

## 3. Deep Failure Analysis & Root Cause Diagnosis

The Phase 2 evaluation unmasked **18 specific failures**. Below is an in-depth diagnostic breakdown of the primary failure modes.

### Failure Cluster 1: Conversational & Terminology Misses in Regex Router (4 Failures)
* **Example (ID 101):** *"Can you tell me what needs to be checked and cleared before we can crank up the hydraulic pump pack?"*
  * **System Response:** Fallback snippet: `"Based on evidence from training_slide_excerpt.pptx: What is the HPU? The Hydraulic Power Unit is the heart of the press's hydraulic system..."`
  * **Expected Ground Truth:** The 4 startup preconditions (fluid level normal, IV-21 open, e-stop reset, maintenance panel closed).
  * **Root Cause:** The question used conversational phrasing (`crank up`) and alternative terminology (`hydraulic pump pack`). Because `start` or `starting` was not matched as an exact substring, the question bypassed the Q1 rule and hit BM25. BM25 retrieved the slide deck overview instead of Section 4.3 of the Operator Manual.
* **Example (ID 115):** *"wat is the normal hpu presure setpoint and whitch docuemnt specifies it?"*
  * **System Response:** Fallback snippet citing ECN-1042 without identifying `operator_manual.pdf`.
  * **Root Cause:** Lexical BM25 tokenizes words verbatim. Typos (`wat`, `presure`, `whitch`, `docuemnt`) degraded BM25 term frequency scores, preventing comprehensive document ranking.

### Failure Cluster 2: Architectural Inability to Perform Multi-Document Synthesis (6 Failures)
* **Example (ID 202):** *"Connecting hydraulic schematic AEG-DWG-H01 and electrical drawing AEG-DWG-E02, what electrical voltage powers the controller monitoring IV-21?"*
  * **System Response:** Fallback snippet citing only `system_diagram_hydraulic.pdf` (Drawing Lines 8 & 9).
  * **Expected Ground Truth:** PLC-03 controls IV-21; PLC-03 is powered by 120VAC / 24VDC derived from 480V via control transformer T1 per AEG-DWG-E02.
  * **Root Cause:** The fallback pipeline is hardcoded to retrieve only the single top-1 chunk (`top_chunk, score, meta = bm25_results[0]`). It has no mechanism to identify that this query spans two distinct domains (hydraulic topology and electrical schematic) and retrieve from both.
* **Example (ID 207):** *"Cross-referencing scanned_appendix_calibration.pdf and wiring_diagram.pdf, what signaling standard (e.g. 4-20mA) and terminal block are used by pressure sensor PS-04A?"*
  * **System Response:** Fallback snippet citing only `scanned_appendix_calibration.pdf` without retrieving Terminal Block TB-7 from `wiring_diagram.pdf`.
  * **Root Cause:** Lack of an iterative multi-hop retrieval loop.

### Failure Cluster 3: Uncritical Acceptance of False Premises (2 Failures)
* **Example (ID 402):** *"What is the recommended maintenance procedure for the pressure sensor PS-40 installed on the HPU discharge line?"*
  * **System Response:** Fallback snippet: `"Based on evidence from training_slide_excerpt.pptx: What is the HPU? The Hydraulic Power Unit is the heart..."` with confidence `HIGH` (0.68).
  * **Expected Ground Truth:** The question contains a false premise: PS-40 is NOT on the HPU discharge line; it is in the Skid B Coolant Loop.
  * **Root Cause:** The QA fallback engine lacks a premise validation layer. When a question mentions an entity (`PS-40`) and an attribute (`maintenance procedure`), the engine blindly queries BM25, retrieves whatever chunks share the words, and outputs them affirmatively without testing premise consistency against the canonical entity register.
* **Example (ID 404):** *"Under what conditions is an operator permitted to reset controller PLC-03 while system pressure is at 100 bar?"*
  * **System Response:** Outputted the 50 bar rule but failed to explicitly declare that the question's premise (resetting at 100 bar) is completely prohibited and invalid.

### Failure Cluster 4: False Positive Confidence & Hallucinated Abstention on Negative Queries (2 Failures)
* **Example (ID 504):** *"What is the acoustic noise emission level in dBA of the HPU pump motor when running at full 200 bar continuous load?"*
  * **System Response:** `"Based on evidence from training_slide_excerpt.pptx: What is the HPU? The Hydraulic Power Unit is the heart of the press's hydraulic system..."` with `abstain=False`, `confidence_status="HIGH"`, `confidence_score=0.74`.
  * **Expected Ground Truth:** The documentation package omits acoustic noise emission ratings. The system MUST abstain (`abstain=True`).
  * **Root Cause:** In Phase 1, negative knowledge tests succeeded because each of the 5 negative queries had dedicated `if` branches checking for specific strings (`temperature`, `voltage sensor`, `ecn-1058`, `mtbf`, `400v`). For an unseen negative question (acoustic noise), the query fell to BM25. High-frequency words (`HPU`, `pump`, `200 bar`) produced a BM25 score of 8.9 (well above the 1.0 threshold), tricking the fallback into asserting that evidence was found and setting `abstain=False`.
* **Example (ID 505):** *"What is the dynamic viscosity of the hydraulic fluid at 120 degrees Celsius according to the system documentation?"*
  * **System Response:** Outputted Section 1 of `legacy_manual_v1.html` with `confidence_status="HIGH"` instead of abstaining.

### Failure Cluster 5: Cross-Firmware Scoping & Adversarial Confusion (2 Failures)
* **Example (ID 601):** *"If a maintenance technician replaces a broken PS-04 with a new PS-04A on a press running firmware 3.1, will it function properly at 200 bar?"*
  * **System Response:** Generated answer stating PS-04 and PS-04A are different, but failed to answer the operational conditional: whether it will function at 200 bar on firmware 3.1 (it cannot; firmware 3.1 only supports 180 bar).
* **Example (ID 602):** *"Can we route the coolant line pressure readings from PS-40 into the HPU A17 alarm logic?"*
  * **System Response:** Retrieved an irrelevant snippet regarding IV-21 from `operator_manual.pdf`.

---

## 4. Engineering Assessment: Genuine Capabilities vs. Architectural Deficits

As senior validation engineers, we must distinguish between what Aegis has genuinely accomplished and where its current architecture relies on superficial heuristics.

```
                    AEGIS MATURITY PROFILE
                    
Capability Area                      Maturity Level
---------------------------------------------------------
1. Heterogeneous File Parsing        [████████████████████] 100% (Robust)
2. Canonical Entity Modeling          [████████████████----]  80% (Verified)
3. Provenance Coordinate Tracking    [██████████████████--]  90% (Verified)
4. Revision Conflict Representation   [██████████████------]  70% (Model-Level)
5. Out-of-Distribution QA Routing    [██████--------------]  30% (Heuristic)
6. Multi-Hop Evidence Synthesis      [████----------------]  20% (Unimplemented)
7. Autonomous Negative Abstention    [██████--------------]  30% (Regex-Guarded)
```

### What Aegis Genuinely Demonstrates:
1. **Exceptional Multi-Modal Extraction**: The ingestion subsystem successfully ingested 20 heterogeneous files across 8 formats (born-digital PDF, scanned PDF with RapidOCR, vector PDF schematics, PNG schematics, DOCX, PPTX, XLSX, JSON) into 372 SQLite chunks with zero data loss and exact coordinates.
2. **Robust Entity Distinction Models**: The canonical registry (`EntityResolver`) correctly models that `PS-04`, `PS-04A`, and `PS-40` are distinct devices and prevents merging them based on string similarity.
3. **Structured Conflict Representation**: The database cleanly represents version-scoped conflicts (180 bar pre-3.2 vs 200 bar post-3.2 vs 175 bar uncalibrated field notes) with explicit trust weights.
4. **Verifiable Citation Grounding**: When the system answers via its structured layer, 84.1% of claims are directly entailed or logically inferred from verified chunks, with 0% direct contradictions.

### What Remains Unverified or Fails:
1. **Absence of Autonomous Semantic Synthesis**: The system does not possess an LLM or neural reader. When a question falls outside the 23 pre-programmed intent patterns, the engine cannot synthesize an answer; it simply copies the first 280 characters of a BM25 chunk.
2. **Brittle Intent Disptach**: The 100% score on the Phase 1 benchmark was largely an artifact of hardcoded `if` statements matching specific keyword combinations. Slight phrasing variations (`crank up the hydraulic pump pack`) cause catastrophic fallback.
3. **Absence of Multi-Document Join Engine**: Outside the hardcoded routes, Aegis cannot autonomously join facts across documents. It cannot answer a query requiring Document A + Document B unless an explicit route was authored.
4. **Superficial Abstention Mechanism**: The system's abstention mechanism does not evaluate semantic sufficiency; it evaluates keyword score thresholds. Consequently, any unanswerable question containing common words (like `pump` or `pressure`) causes false-positive hallucinations.

---

## 5. Architectural Recommendations for Phase 3

To achieve true industrial-grade generalization without paid external APIs, we recommend the following enhancements:

1. **Replace Keyword Routing with a Local Dense Bi-Encoder (BGE-Small / MiniLM)**:
   * Replace the regex `if/elif` chain with a quantized local embedding model (ONNX runtime, $<100\text{ MB}$, zero cloud dependencies).
   * This will resolve conversational synonyms (`crank up` $\leftrightarrow$ `start`), typos (`presure` $\leftrightarrow$ `pressure`), and indirect questions.
2. **Implement Iterative Multi-Hop Graph Retrieval**:
   * For multi-document queries, retrieve initial entity anchors from the structured graph, identify missing topological links (e.g., PLC-03 $\rightarrow$ T1 $\rightarrow$ 480V), and traverse relationships across schematics rather than relying on single BM25 chunks.
3. **Premise Verification Gate**:
   * Before generating an answer, run a sanity-check pass that validates whether question assertions match the canonical entity registry (e.g., verifying whether `PS-40` actually belongs to `HPU` before retrieving maintenance procedures).
4. **Semantic Sufficiency Abstention Filter**:
   * Instead of checking `BM25_score > 1.0`, verify whether the retrieved chunk contains the *target attribute* (e.g., checking for temperature units `°C`/`°F` when asked for temperature, or decibel units `dBA` when asked for noise). If the target attribute is absent from all retrieved chunks, trigger honest abstention.

---

## 6. Audit Verification Sign-Off

* **Original 23-Question Benchmark:** Retained, isolated, and verified at **100.0% accuracy**.
* **Phase 1 Automated Test Suite:** 38/38 passing, completely unmodified.
* **Phase 2 Robustness Test Suite:** 10/10 new automated tests passing (Total: **48/48 automated tests passing** in 0.32s).
* **Evaluation Artifacts:** Persisted to `data/processed/phase2_evaluation_results.json` and `reports/phase2_robustness_report.md`.

*Report compiled and certified by Senior AI Systems Validation Engineering.*

