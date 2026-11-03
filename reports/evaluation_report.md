# AEGIS KNOWLEDGE INTELLIGENCE SYSTEM — EVALUATION REPORT

## 1. Executive Summary & Benchmark Metrics

The Aegis evaluation suite benchmarks the system against 23 multi-modal, version-sensitive, and negative-constraint questions derived directly from `evaluation-questions.pdf`. The framework strictly separates document existence from verifiable evidence grounding and enforces uncompromising abstention correctness.

### Core Performance Metrics
- **Overall Answer Accuracy**: **100.0%** (23/23)
- **Positive-Question Accuracy (Q1–Q18)**: **100.0%** (18/18)
- **Negative-Question Abstention Accuracy (Q19–Q23)**: **100.0%** (5/5)
- **Citation Document Validity Rate**: **100.0%** (23/23)
- **Evidence Grounding Validity Rate**: **100.0%** (23/23)
- **Question Coverage**: **100.0%** (23/23)

> [!IMPORTANT]
> **Document Existence vs. Evidence Grounding Distinction**:
> - **Document Validity**: Validates that all cited documents exist within the 20-file ingested Aegis dataset.
> - **Evidence Grounding Validity**: Rigorously requires that the cited document exists, matches the expected authoritative source, specifies granular coordinates (Page, Sheet, Cell, JSON path), and contains verifiable factual grounding within SQLite database chunks.

---

## 2. Granular Question-by-Question Scorecard

| ID | Question | Focus Entity | Status | Doc Exists | Grounded | Abstain OK | Confidence |
|---|---|---|---|---|---|---|---|
| Q1 | What must be true before starting the Hydr... | `HPU` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q2 | What is the current normal operating press... | `HPU` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q3 | What does alarm A17 indicate, and what are... | `A17` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q4 | Is PS-04 the same component as PS-04A?... | `PS-04` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q5 | Which document introduced the change from ... | `PS-04A` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q6 | Which components connect directly to the H... | `PLC-03` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q7 | What action is required if alarm A17 persi... | `A17` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q8 | Under what circumstances must the controll... | `PLC-03` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q9 | What was the operating pressure threshold ... | `HPU` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q10 | Which alarm is associated with a pressure ... | `A17` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q11 | According to the component register, what ... | `IV-21` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q12 | Does the training slide deck introduce any... | `Auxiliary Reservoir` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q13 | What sensor ID appears on the diagnostics ... | `PS-04A` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q14 | Per the revision history, when did softwar... | `Software Revision 3.2` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q15 | What does sensor_ps04a_threshold_bar in th... | `PS-04A` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q16 | Does the 200 bar threshold apply to all Ae... | `HPU` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q17 | Is PS-04 the same as PS-40?... | `PS-40` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q18 | What was the pressure limit before revisio... | `HPU` | **PASS** | VALID | GROUNDED | CORRECT | HIGH |
| Q19 | What is the maximum continuous operating t... | `PS-04A` | **PASS** | VALID | GROUNDED | CORRECT | UNANSWERABLE / ABSTAIN |
| Q20 | What is the calibration interval for the e... | `Electrical System Diagram` | **PASS** | VALID | GROUNDED | CORRECT | UNANSWERABLE / ABSTAIN |
| Q21 | Who approved engineering bulletin ECN-1058... | `ECN-1058` | **PASS** | VALID | GROUNDED | CORRECT | UNANSWERABLE / ABSTAIN |
| Q22 | What is the mean time between failures for... | `IV-21` | **PASS** | VALID | GROUNDED | CORRECT | UNANSWERABLE / ABSTAIN |
| Q23 | Is the Aegis Series-7 HCS compatible with ... | `Aegis Series-7 HCS` | **PASS** | VALID | GROUNDED | CORRECT | UNANSWERABLE / ABSTAIN |

---

## 3. Detailed Audit of Responses, Evidence & Provenance

### Question 1: What must be true before starting the Hydraulic Power Unit?
- **Focus Entity**: `HPU`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: Before starting the Hydraulic Power Unit (HPU), four conditions must be satisfied: (1) Hydraulic fluid level must be within the normal band on the sight glass; (2) Isolation valve IV-21 must be OPEN; (3) The emergency stop circuit must be RESET; and (4) The maintenance access panel must be CLOSED (starting with the panel removed exposes rotating components).
- **Key Claims**:
  - Hydraulic fluid level must be within the normal band on the sight glass.
  - Isolation valve IV-21 must be OPEN.
  - The emergency stop (E-stop) circuit must be RESET.
  - The maintenance access panel must be CLOSED / installed (WARNING: rotating parts inside HPU housing are exposed if removed).
- **Provenance Sources**:
  - Document: `manuals/operator_manual.pdf` | Location: `Section 4.3 (Starting the Hydraulic Power Unit), Page 1` | Method: `pymupdf_text` | Trust: `OFFICIAL`
  - Document: `configuration/configuration_export.json` | Location: `startup_interlocks (valve_iv21_required_state, estop_required_state, maintenance_panel_required_state, fluid_level_required_band)` | Method: `json_leaf_extraction` | Trust: `SYSTEM_CONFIG`
  - Document: `screenshots/screen_01_home.png` | Location: `STARTUP INTERLOCKS panel: IV-21 OPEN, Emergency Stop RESET, Maintenance Panel CLOSED, Fluid Level NORMAL` | Method: `rapidocr` | Trust: `VERIFIED_RECORD`
- **Engineering Notes**: All 4 startup interlocks must be verified before start.

### Question 2: What is the current normal operating pressure for the HPU, and under what conditions does that apply?
- **Focus Entity**: `HPU`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: The current normal operating pressure for the HPU is 200 bar. This setpoint applies specifically to units running software revision 3.2 and later equipped with pressure sensor PS-04A (introduced per ECN-1042 for Series-7 units manufactured after 2024). Units running earlier software revisions (< 3.2) operate at 180 bar with the original PS-04 sensor.
- **Key Claims**:
  - Current normal operating pressure for the HPU is 200 bar.
  - This setpoint applies to units running software revision 3.2 and later (equipped with pressure sensor PS-04A, manufactured after 2024).
  - Historical note: on software revisions prior to 3.2 (with sensor PS-04), normal operating pressure was 180 bar.
  - Field observation caveat: site survey notes recorded 175 bar on an uncalibrated Line 4 gauge, which does not supersede the 200 bar specification.
- **Provenance Sources**:
  - Document: `manuals/operator_manual.pdf` | Location: `Section 4.3 & Section 5 (Normal Operating Ranges), Page 1` | Method: `pymupdf_text` | Trust: `OFFICIAL`
  - Document: `engineering_bulletins/ECN-1042.pdf` | Location: `Section 1 (Description of Change)` | Method: `pymupdf_text` | Trust: `AUTHORITATIVE_BULLETIN`
  - Document: `configuration/configuration_export.json` | Location: `sensors.sensor_ps04a_threshold_bar (value: 200)` | Method: `json_leaf_extraction` | Trust: `SYSTEM_CONFIG`
- **Engineering Notes**: 200 bar setpoint applies to firmware >= 3.2; earlier revisions operated at 180 bar.

### Question 3: What does alarm A17 indicate, and what are its possible causes?
- **Focus Entity**: `A17`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: Alarm A17 indicates that HPU hydraulic discharge pressure has fallen below 150 bar (Hydraulic Pressure Low). Its documented possible causes are: (1) Isolation valve IV-21 is closed or partially closed; (2) Hydraulic fluid level is low in the reservoir; and (3) The pressure sensor signal is invalid or out of calibration.
- **Key Claims**:
  - Alarm A17 indicates low hydraulic pressure (discharge pressure below 150 bar).
  - Possible cause 1: Isolation valve IV-21 closed or partially closed.
  - Possible cause 2: Low hydraulic fluid level in reservoir.
  - Possible cause 3: Pressure sensor signal invalid or out of calibration (see Alarm A19).
- **Provenance Sources**:
  - Document: `reference/alarm_reference.pdf` | Location: `Alarm Reference Table, Row A17, Page 1` | Method: `pymupdf_text` | Trust: `OFFICIAL`
  - Document: `manuals/maintenance_manual.pdf` | Location: `Section 6 (Troubleshooting: Low Discharge Pressure), Page 1` | Method: `pymupdf_text` | Trust: `OFFICIAL`
- **Engineering Notes**: Pressure < 150 bar. Three primary causes listed in Alarm Reference.

### Question 4: Is PS-04 the same component as PS-04A?
- **Focus Entity**: `PS-04`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: No, PS-04 is not the same component as PS-04A. PS-04 was the original pressure sensor (operating at 180 bar), which was superseded by PS-04A effective software revision 3.2 per Engineering Change Notice ECN-1042. PS-04A features an updated signal conditioning circuit to eliminate signal drift, operates at a 200 bar setpoint, and is not a form-fit-function replacement, requiring controller firmware 3.2 or later.
- **Key Claims**:
  - PS-04 and PS-04A are NOT the same component.
  - PS-04 was the original HPU discharge pressure sensor (operating target: 180 bar).
  - PS-04A is an updated pressure sensor with redesigned signal conditioning circuitry to fix drift issues, operating at a 200 bar target.
  - PS-04A is not a form-fit-function equivalent; it requires controller firmware revision 3.2 or later.
- **Provenance Sources**:
  - Document: `engineering_bulletins/ECN-1042.pdf` | Location: `Section 1 (Description of Change) & Section 2 (Reason for Change)` | Method: `pymupdf_text` | Trust: `AUTHORITATIVE_BULLETIN`
  - Document: `reference/component_register.xlsx` | Location: `Worksheet: Components, Rows 4 and 5` | Method: `openpyxl_sheet` | Trust: `OFFICIAL`
- **Engineering Notes**: PS-04 superseded by PS-04A due to signal drift after 18 months.

### Question 5: Which document introduced the change from PS-04 to PS-04A?
- **Focus Entity**: `PS-04A`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: Engineering Change Notice ECN-1042 ('Pressure Sensor Replacement (PS-04 -> PS-04A) and Operating Pressure Update') introduced the change from PS-04 to PS-04A, taking effect with software revision 3.2.
- **Key Claims**:
  - The change from PS-04 to PS-04A was introduced by Engineering Change Notice ECN-1042.
  - Title: 'Pressure Sensor Replacement (PS-04 -> PS-04A) and Operating Pressure Update'.
  - Effective: Software Revision 3.2 (Release date: 2025-09-30).
- **Provenance Sources**:
  - Document: `engineering_bulletins/ECN-1042.pdf` | Location: `Document Title and Section 1` | Method: `pymupdf_text` | Trust: `AUTHORITATIVE_BULLETIN`
  - Document: `reference/revision_history.xlsx` | Location: `Worksheet: Revision History, Row 4 (Software Rev 3.2)` | Method: `openpyxl_sheet` | Trust: `OFFICIAL`
- **Engineering Notes**: Engineering Change Notice ECN-1042 enacted effective software revision 3.2.

### Question 6: Which components connect directly to the HCS controller, according to the hydraulic schematic?
- **Focus Entity**: `PLC-03`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: According to the hydraulic schematic (AEG-DWG-H01), the components that connect directly to the HCS Controller (PLC-03) via control/signal lines (purple lines) are PS-04A (pressure sensor) and IV-21 (isolation valve). Additionally, the schematic depicts a grey line between PLC-03 and the HPU; however, per the drawing legend, grey lines represent hydraulic fluid paths, making this direct connection anomalous and flagged for manual engineering review.
- **Key Claims**:
  - According to the hydraulic schematic (AEG-DWG-H01) legend, purple lines represent control/signal connections to PLC-03.
  - Two components connect directly to PLC-03 via verified purple signal lines: PS-04A (discharge pressure sensor) and IV-21 (isolation valve).
  - Topological anomaly / uncertain edge: A grey line (legend: hydraulic fluid path) is also drawn between PLC-03 and the Hydraulic Power Unit (HPU). Because electronic controllers do not carry hydraulic fluid, this line is flagged as UNCERTAIN_EDGE_FLAGGED_FOR_REVIEW.
- **Provenance Sources**:
  - Document: `diagrams/system_diagram_hydraulic.pdf` | Location: `AEG-DWG-H01, Drawing Lines 8 & 9 (Purple signal connections) and Drawing Line 7 (Grey fluid line)` | Method: `vector_shape_analysis` | Trust: `OFFICIAL`
- **Engineering Notes**: Purple control lines connect directly to PS-04A and IV-21. Grey fluid line to HPU is an uncertain edge for manual review.

### Question 7: What action is required if alarm A17 persists for more than 10 seconds?
- **Focus Entity**: `A17`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: If Alarm A17 persists for more than 10 seconds, the required action is to immediately execute Shutdown Procedure 4.7: close isolation valve IV-21, confirm pressure decay, set the POWER selector to OFF, tag out the system per site lockout/tagout procedures, and proceed to troubleshooting. Silencing the alarm alone is prohibited.
- **Key Claims**:
  - If alarm A17 persists for more than 10 seconds, operator must execute Shutdown Procedure 4.7.
  - Shutdown Procedure 4.7: Close IV-21, confirm pressure decay, set POWER selector to OFF, and tag out per site lockout/tagout procedure.
  - Do not attempt to clear a persistent A17 by silencing the alarm alone.
- **Provenance Sources**:
  - Document: `manuals/maintenance_manual.pdf` | Location: `Section 4 (Alarm A17 Response), Page 1` | Method: `pymupdf_text` | Trust: `OFFICIAL`
  - Document: `reference/alarm_reference.pdf` | Location: `Alarm Reference Table Footnote (*), Page 1` | Method: `pymupdf_text` | Trust: `OFFICIAL`
  - Document: `configuration/configuration_export.json` | Location: `alarms.A17.persistence_before_shutdown_seconds (value: 10, procedure_ref: 4.7)` | Method: `json_leaf_extraction` | Trust: `SYSTEM_CONFIG`
- **Engineering Notes**: Execute Procedure 4.7; silencing alarm alone is prohibited.

### Question 8: Under what circumstances must the controller not be reset?
- **Focus Entity**: `PLC-03`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: The PLC-03 controller must NOT be reset while hydraulic pressure is above 50 bar. Resetting the controller under pressure re-initializes valve driver outputs, which can trigger an uncommanded actuation of Isolation Valve IV-21. The circuit must be manually bled below 50 bar before a reset is performed; firmware actively blocks reset commands above 50 bar.
- **Key Claims**:
  - The PLC-03 controller must NOT be reset while hydraulic pressure is above 50 bar.
  - Reason: The reset routine re-initializes valve driver outputs, which can produce a momentary uncommanded actuation/transition of Isolation Valve IV-21 if the circuit is still pressurized.
  - Pressure must first be bled below 50 bar using the manual bleed procedure before resetting.
- **Provenance Sources**:
  - Document: `manuals/operator_manual.pdf` | Location: `Section 7 (Controller Reset), Page 1` | Method: `pymupdf_text` | Trust: `OFFICIAL`
  - Document: `manuals/maintenance_manual.pdf` | Location: `Section 3 (Controller Reset Conditions), Page 1` | Method: `pymupdf_text` | Trust: `OFFICIAL`
  - Document: `configuration/configuration_export.json` | Location: `controller_reset.max_pressure_bar_allowed_for_reset (value: 50)` | Method: `json_leaf_extraction` | Trust: `SYSTEM_CONFIG`
- **Engineering Notes**: Must not reset when pressure is > 50 bar to prevent uncommanded valve transition.

### Question 9: What was the operating pressure threshold before software revision 3.2, and what changed it?
- **Focus Entity**: `HPU`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: Before software revision 3.2, the normal operating pressure threshold was 180 bar. It was changed to 200 bar by Engineering Change Notice ECN-1042 alongside the replacement of sensor PS-04 with PS-04A, implemented as a process improvement to accelerate press cycle times.
- **Key Claims**:
  - Before software revision 3.2, the normal operating pressure threshold was 180 bar.
  - It was changed to 200 bar by Engineering Change Notice ECN-1042.
  - The change was a deliberate process change to improve press cycle times on Series-7 units manufactured after 2024, enacted concurrently with the replacement of sensor PS-04 by PS-04A.
- **Provenance Sources**:
  - Document: `engineering_bulletins/ECN-1042.pdf` | Location: `Section 1 (Description of Change)` | Method: `pymupdf_text` | Trust: `AUTHORITATIVE_BULLETIN`
  - Document: `manuals/operator_manual.pdf` | Location: `Section 5 (Normal Operating Ranges), Page 1-2` | Method: `pymupdf_text` | Trust: `OFFICIAL`
  - Document: `manuals/legacy_manual_v1.html` | Location: `Section 5 (Normal Operating Ranges)` | Method: `bs4_html` | Trust: `OFFICIAL_SUPERSEDED`
  - Document: `configuration/configuration_export.json` | Location: `revision_applicability.sensor_ps04_legacy_threshold_bar (value: 180)` | Method: `json_leaf_extraction` | Trust: `SYSTEM_CONFIG`
- **Engineering Notes**: Was 180 bar; changed to 200 bar by ECN-1042.

### Question 10: Which alarm is associated with a pressure sensor reading below 150 bar?
- **Focus Entity**: `A17`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: Alarm A17 (Hydraulic Pressure Low) is associated with a pressure sensor reading below 150 bar.
- **Key Claims**:
  - Alarm A17 (Hydraulic Pressure Low) is triggered when pressure falls below 150 bar.
  - Panel indication is RED.
  - Evaluated against whichever pressure sensor is active for the software revision (PS-04 or PS-04A per ECN-1058).
- **Provenance Sources**:
  - Document: `reference/alarm_reference.pdf` | Location: `Alarm Reference Table, Row A17` | Method: `pymupdf_text` | Trust: `OFFICIAL`
  - Document: `configuration/configuration_export.json` | Location: `sensors.sensor_ps04a_alarm_low_bar (value: 150)` | Method: `json_leaf_extraction` | Trust: `SYSTEM_CONFIG`
- **Engineering Notes**: Alarm A17 (Hydraulic Pressure Low).

### Question 11: According to the component register, what is the location of the isolation valve IV-21?
- **Focus Entity**: `IV-21`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: According to the Component Register (AEG-CR-700), the location of the isolation valve IV-21 is the 'Hydraulic Module'.
- **Key Claims**:
  - According to the component register, the location of isolation valve IV-21 is the 'Hydraulic Module'.
- **Provenance Sources**:
  - Document: `reference/component_register.xlsx` | Location: `Worksheet: Components, Row 3, Cell D3 (Location: 'Hydraulic Module')` | Method: `openpyxl_sheet` | Trust: `OFFICIAL`
- **Engineering Notes**: Location listed verbatim as 'Hydraulic Module' in AEG-CR-700.

### Question 12: Does the training slide deck introduce any component or alarm not found in the manuals?
- **Focus Entity**: `Auxiliary Reservoir`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: Yes, the training slide deck introduces the 'Auxiliary Reservoir', a component not found in the standard Operator Manual. Slide 2 explicitly notes that the Auxiliary Reservoir is a Line 4/5-specific configuration detail for topping up fluid during peak demand, and is omitted from the standard manual. The deck does not introduce any new alarms.
- **Key Claims**:
  - The training slide deck introduces the 'Auxiliary Reservoir', which is not found in the standard Operator Manual.
  - Slide 2 explicitly notes: 'Auxiliary Reservoir is a Line 4/5-specific configuration detail and is not covered in the standard Operator Manual.'
  - The slide deck does not introduce any new alarms.
- **Provenance Sources**:
  - Document: `extra/training_slide_excerpt.pptx` | Location: `Slide 2 ('What is the HPU?' and bottom Note)` | Method: `python_pptx` | Trust: `VERIFIED_RECORD`
- **Engineering Notes**: Introduces Auxiliary Reservoir for Line 4/5 peak demand top-up.

### Question 13: What sensor ID appears on the diagnostics screenshot, and does it match a known component?
- **Focus Entity**: `PS-04A`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: The sensor ID that appears on the diagnostics screenshot is 'P.S. 04-A' (or 'P.S.04-A'). Yes, it matches the known canonical component PS-04A (HPU discharge pressure sensor). An explanatory note at the bottom of the diagnostics screen explicitly clarifies that this screen displays the tag as printed on the physical unit label.
- **Key Claims**:
  - The sensor ID that appears on the diagnostics screenshot is 'P.S. 04-A' (or 'P.S.04-A').
  - Yes, this matches known component PS-04A (the HPU discharge pressure sensor).
  - The diagnostics screen explicitly provides a note explaining: 'this screen displays the sensor tag as printed on the physical unit label', confirming that 'P.S. 04-A' is the verbatim physical label formatting of PS-04A.
- **Provenance Sources**:
  - Document: `screenshots/screen_03_diagnostics.png` | Location: `Tag field ('P.S. 04-A') and bottom note text` | Method: `rapidocr` | Trust: `VERIFIED_RECORD`
  - Document: `reference/component_register.xlsx` | Location: `Worksheet: Components, Row 4 (PS-04A)` | Method: `openpyxl_sheet` | Trust: `OFFICIAL`
- **Engineering Notes**: Displays 'P.S. 04-A', which matches PS-04A per on-screen physical label note.

### Question 14: Per the revision history, when did software revision 3.2 take effect, and what changed alongside it?
- **Focus Entity**: `Software Revision 3.2`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: Per the Revision History (and ECN-1042), software revision 3.2 took effect on September 30, 2025 (2025-09-30). Alongside this release, pressure sensor PS-04 was replaced by PS-04A, and the normal HPU discharge pressure setpoint was increased from 180 bar to 200 bar.
- **Key Claims**:
  - Software revision 3.2 took effect on September 30, 2025 (2025-09-30).
  - Alongside it, pressure sensor PS-04 was replaced by PS-04A.
  - The normal HPU discharge pressure setpoint was updated from 180 bar to 200 bar per ECN-1042.
- **Provenance Sources**:
  - Document: `reference/revision_history.xlsx` | Location: `Worksheet: Revision History, Row 4 (Cells A4:D4)` | Method: `openpyxl_sheet` | Trust: `OFFICIAL`
  - Document: `engineering_bulletins/ECN-1042.pdf` | Location: `ECN Header & Section 1` | Method: `pymupdf_text` | Trust: `AUTHORITATIVE_BULLETIN`
- **Engineering Notes**: Took effect 2025-09-30. Replaced PS-04 with PS-04A, changed setpoint to 200 bar.

### Question 15: What does sensor_ps04a_threshold_bar in the configuration export correspond to in the operator manual's terminology?
- **Focus Entity**: `PS-04A`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: In the configuration export, 'sensor_ps04a_threshold_bar' (set to 200 bar) corresponds to the 'normal operating pressure' (or 'normal HPU discharge pressure setpoint') in the Operator Manual's terminology.
- **Key Claims**:
  - In configuration_export.json, 'sensor_ps04a_threshold_bar' has a value of 200.
  - In the Operator Manual (AEG-OM-700), this corresponds to 'normal operating pressure' (or 'normal HPU discharge pressure setpoint').
- **Provenance Sources**:
  - Document: `configuration/configuration_export.json` | Location: `sensors.sensor_ps04a_threshold_bar (value: 200)` | Method: `json_leaf_extraction` | Trust: `SYSTEM_CONFIG`
  - Document: `manuals/operator_manual.pdf` | Location: `Section 4.3 (Startup sequence step 3) & Section 5 (Normal Operating Ranges), Page 1` | Method: `pymupdf_text` | Trust: `OFFICIAL`
- **Engineering Notes**: Corresponds to 'normal operating pressure' / setpoint (200 bar).

### Question 16: Does the 200 bar threshold apply to all Aegis HCS units, or only some?
- **Focus Entity**: `HPU`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: The 200 bar threshold applies only to SOME Aegis HCS units. It applies strictly to units running software revision 3.2 or later (equipped with sensor PS-04A, manufactured after 2024). Units operating on software revisions earlier than 3.2 retain sensor PS-04 and operate under the 180 bar threshold.
- **Key Claims**:
  - The 200 bar threshold applies only to SOME Aegis HCS units, not all.
  - It applies specifically to units running software revision 3.2 and later (with sensor PS-04A installed, manufactured after 2024).
  - Units running firmware prior to revision 3.2 continue to use sensor PS-04 and operate at the 180 bar setpoint.
- **Provenance Sources**:
  - Document: `engineering_bulletins/ECN-1042.pdf` | Location: `Section 1 (Description of Change)` | Method: `pymupdf_text` | Trust: `AUTHORITATIVE_BULLETIN`
  - Document: `manuals/operator_manual.pdf` | Location: `Section 5 (Normal Operating Ranges), Page 1-2` | Method: `pymupdf_text` | Trust: `OFFICIAL`
  - Document: `configuration/configuration_export.json` | Location: `revision_applicability (applies_from_firmware: '3.2' vs applies_before_firmware: '3.2')` | Method: `json_leaf_extraction` | Trust: `SYSTEM_CONFIG`
- **Engineering Notes**: Only units running revision >= 3.2 with PS-04A installed.

### Question 17: Is PS-04 the same as PS-40?
- **Focus Entity**: `PS-40`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: No, PS-04 is completely distinct from PS-40. PS-04 is the original (now superseded) discharge pressure sensor on the HPU located on Skid A. PS-40 is a sensor located on Skid B dedicated to the Coolant Loop, completely separate from the HPU circuit. The machine configuration dump explicitly instructs that PS-40 is unrelated to the HPU and must never be confused with PS-04.
- **Key Claims**:
  - No, PS-04 is NOT the same as PS-40.
  - PS-04 is the superseded pressure sensor for the HPU discharge line on Skid A.
  - PS-40 is a pressure sensor in the Coolant Loop on Skid B, completely unrelated to the HPU discharge circuit.
  - The configuration export explicitly warns: 'unrelated to HPU discharge circuit; do not map to sensor_ps04a_* keys'.
- **Provenance Sources**:
  - Document: `reference/component_register.xlsx` | Location: `Worksheet: Components, Rows 4 and 6` | Method: `openpyxl_sheet` | Trust: `OFFICIAL`
  - Document: `configuration/configuration_export.json` | Location: `sensors.sensor_ps40_zone & sensor_ps40_note` | Method: `json_leaf_extraction` | Trust: `SYSTEM_CONFIG`
- **Engineering Notes**: Completely separate components: PS-04 on Skid A HPU; PS-40 on Skid B Coolant Loop.

### Question 18: What was the pressure limit before revision 3.2?
- **Focus Entity**: `HPU`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `False`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: Before software revision 3.2, the normal operating pressure threshold was 180 bar. It was changed to 200 bar by Engineering Change Notice ECN-1042 alongside the replacement of sensor PS-04 with PS-04A, implemented as a process improvement to accelerate press cycle times.
- **Key Claims**:
  - Before software revision 3.2, the normal operating pressure threshold was 180 bar.
  - It was changed to 200 bar by Engineering Change Notice ECN-1042.
  - The change was a deliberate process change to improve press cycle times on Series-7 units manufactured after 2024, enacted concurrently with the replacement of sensor PS-04 by PS-04A.
- **Provenance Sources**:
  - Document: `engineering_bulletins/ECN-1042.pdf` | Location: `Section 1 (Description of Change)` | Method: `pymupdf_text` | Trust: `AUTHORITATIVE_BULLETIN`
  - Document: `manuals/operator_manual.pdf` | Location: `Section 5 (Normal Operating Ranges), Page 1-2` | Method: `pymupdf_text` | Trust: `OFFICIAL`
  - Document: `manuals/legacy_manual_v1.html` | Location: `Section 5 (Normal Operating Ranges)` | Method: `bs4_html` | Trust: `OFFICIAL_SUPERSEDED`
  - Document: `configuration/configuration_export.json` | Location: `revision_applicability.sensor_ps04_legacy_threshold_bar (value: 180)` | Method: `json_leaf_extraction` | Trust: `SYSTEM_CONFIG`
- **Engineering Notes**: Normal operating pressure setpoint was 180 bar prior to rev 3.2.

### Question 19: What is the maximum continuous operating temperature of PS-04A?
- **Focus Entity**: `PS-04A`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `True`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: The documentation does not specify the maximum continuous operating temperature for pressure sensor PS-04A. While calibration records, electrical specifications (4-20mA), and pressure setpoints (200 bar) are documented across ECN-1042, the manuals, and the scanned calibration appendix, thermal operating limits are absent from the provided package.
- **Key Claims**:
  - Maximum continuous operating temperature for PS-04A is absent from all documents in the package.
- **Provenance Sources**:
  - Document: `All Package Documents` | Location: `Exhaustive corpus review (ECN-1042, scanned_appendix_calibration.pdf, operator_manual.pdf)` | Method: `exhaustive_absence_verification` | Trust: `OFFICIAL`
- **Engineering Notes**: UNANSWERABLE: Thermal operating limits are absent from the package. System must abstain.

### Question 20: What is the calibration interval for the electrical system diagram's voltage sensor?
- **Focus Entity**: `Electrical System Diagram`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `True`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: The documentation does not provide a calibration interval for a voltage sensor. In fact, the electrical schematic (AEG-DWG-E02) does not include a 'voltage sensor' (it contains incoming disconnect Q1, control transformer T1, and power supplies). Furthermore, calibration records in the package explicitly state that recalibration intervals are not included in the binder.
- **Key Claims**:
  - No 'voltage sensor' is present on the electrical schematic (AEG-DWG-E02).
  - No calibration interval is documented in the electrical drawing or anywhere in the documentation package.
  - Scanned calibration appendix notes that calibration intervals are not included in this binder.
- **Provenance Sources**:
  - Document: `diagrams/system_diagram_electrical.png` | Location: `Electrical Schematic AEG-DWG-E02` | Method: `rapidocr` | Trust: `OFFICIAL`
  - Document: `scans/scanned_appendix_calibration.pdf` | Location: `Footer Note: 'No calibration interval is specified...'` | Method: `rapidocr` | Trust: `VERIFIED_RECORD`
- **Engineering Notes**: UNANSWERABLE / FALSE PREMISE: Electrical drawing has no voltage sensor; calibration interval is omitted.

### Question 21: Who approved engineering bulletin ECN-1058?
- **Focus Entity**: `ECN-1058`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `True`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: The documentation does not state who approved engineering bulletin ECN-1058. While ECN-1058 records its status as 'Released' and references ECN-1042, it does not include an approval block, author name, or signature line.
- **Key Claims**:
  - ECN-1058 does not contain an approval block, author name, or sign-off signature.
- **Provenance Sources**:
  - Document: `engineering_bulletins/ECN-1058.pdf` | Location: `Page 1 Header Block` | Method: `pymupdf_text` | Trust: `AUTHORITATIVE_BULLETIN`
- **Engineering Notes**: UNANSWERABLE: ECN-1058 has status Released but omits approver/author identity.

### Question 22: What is the mean time between failures for the isolation valve IV-21?
- **Focus Entity**: `IV-21`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `True`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: The documentation does not provide the mean time between failures (MTBF) for isolation valve IV-21. While the Component Register, manuals, and schematics document its location (Hydraulic Module), required startup state (OPEN), and shutdown procedure (Procedure 4.7), MTBF reliability metrics are not included in the package.
- **Key Claims**:
  - Mean time between failures (MTBF) for IV-21 is not documented in any package file.
- **Provenance Sources**:
  - Document: `All Package Documents` | Location: `Exhaustive search across component_register.xlsx, maintenance_manual.pdf, and operator_manual.pdf` | Method: `exhaustive_absence_verification` | Trust: `OFFICIAL`
- **Engineering Notes**: UNANSWERABLE: MTBF reliability figures for IV-21 are absent from documentation.

### Question 23: Is the Aegis Series-7 HCS compatible with a 3-phase 400V supply?
- **Focus Entity**: `Aegis Series-7 HCS`
- **Correctness**: PASSED
- **Abstention Decision**: CORRECT (Expected Abstain: `True`)
- **Citation Document Validity**: YES
- **Evidence Grounding Validity**: YES
- **Citation Audit Reason**: Citations verified and grounded.
- **Direct Answer**: The documentation does not establish compatibility with a 3-phase 400V supply. The system's electrical specifications consistently prescribe a 480V supply: incoming disconnect Q1 is specified as a '480V incoming disconnect' and control transformer T1 is specified as '480:120V control power'. Operation on a 400V 3-phase supply is unstated and unsupported in the provided documents.
- **Key Claims**:
  - The electrical drawing (AEG-DWG-E02) and component register prescribe a 480V incoming supply (Q1: 480V disconnect; T1: 480:120V control transformer).
  - Compatibility with a 3-phase 400V supply is not documented or supported in the documentation package.
- **Provenance Sources**:
  - Document: `reference/component_register.xlsx` | Location: `Worksheet: Components, Rows 11 and 12 (Q1 and T1)` | Method: `openpyxl_sheet` | Trust: `OFFICIAL`
  - Document: `diagrams/system_diagram_electrical.png` | Location: `Schematic AEG-DWG-E02 (Labels: Q1 MAINDISCONNECT, T1 480:120V)` | Method: `rapidocr` | Trust: `OFFICIAL`
- **Engineering Notes**: UNANSWERABLE / UNSUPPORTED: System specifies 480V supply; 400V compatibility is unsupported in docs.
