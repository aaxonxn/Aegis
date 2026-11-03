"""
Phase 2 Ground Truth Benchmark Specification: Robustness, Generalization & Adversarial Testing.
Defines 45 unseen questions across 5 core categories + targeted adversarial scenarios:
1. Semantically Rephrased Factual (15 questions)
2. Multi-Document Reasoning (10 questions)
3. Entity Disambiguation (5 questions)
4. False-Premise Detection (5 questions)
5. Unanswerable / Abstention (5 questions)
6. Targeted Adversarial Scenarios (5 questions)

None of these questions reuse the exact wording of the original 23 benchmark questions.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Phase2EvaluationItem(BaseModel):
    id: int
    category: str  # "SEMANTIC_REPHRASED", "MULTI_DOC_REASONING", "ENTITY_DISAMBIGUATION", "FALSE_PREMISE", "UNANSWERABLE_ABSTENTION", "ADVERSARIAL"
    question: str
    variation_type: str  # "conversational", "terminology", "abbreviation", "indirect", "misspelling", "combined_facts", "cross_doc", "adversarial_scoping", "false_assumption"
    expected_criteria: List[str]
    expected_abstain: bool
    is_false_premise: bool = False
    expected_sources: List[str]
    focus_entity: str
    ground_truth_answer: str
    notes: str = ""


PHASE2_QUESTIONS_SPEC: List[Phase2EvaluationItem] = [
    # =========================================================================
    # CATEGORY 1: Semantically Rephrased Factual Questions (15 Questions)
    # =========================================================================
    Phase2EvaluationItem(
        id=101,
        category="SEMANTIC_REPHRASED",
        question="Can you tell me what needs to be checked and cleared before we can crank up the hydraulic pump pack?",
        variation_type="conversational",
        expected_criteria=[
            "fluid level normal",
            "iv-21 open",
            "emergency stop reset",
            "maintenance panel closed"
        ],
        expected_abstain=False,
        expected_sources=["operator_manual.pdf", "configuration_export.json", "screen_01_home.png"],
        focus_entity="HPU",
        ground_truth_answer="Before starting the HPU, 4 startup conditions must be met: hydraulic fluid level in normal band, IV-21 open, e-stop reset, and maintenance panel closed.",
        notes="Conversational rephrasing of startup preconditions (Q1 counterpart)."
    ),
    Phase2EvaluationItem(
        id=102,
        category="SEMANTIC_REPHRASED",
        question="What is the targeted fluid pressure for the HPU on units operating with firmware 3.2 or above?",
        variation_type="terminology",
        expected_criteria=[
            "200 bar",
            "3.2"
        ],
        expected_abstain=False,
        expected_sources=["operator_manual.pdf", "ECN-1042.pdf", "configuration_export.json"],
        focus_entity="HPU",
        ground_truth_answer="The targeted fluid pressure is 200 bar, applicable to units running software revision 3.2 or later with PS-04A.",
        notes="Alternative technical terminology ('targeted fluid pressure', 'firmware 3.2 or above')."
    ),
    Phase2EvaluationItem(
        id=103,
        category="SEMANTIC_REPHRASED",
        question="Alarm A-17 went off on my console; what are the potential mechanical and electrical reasons for this alert?",
        variation_type="conversational",
        expected_criteria=[
            "low hydraulic pressure",
            "iv-21",
            "fluid",
            "sensor"
        ],
        expected_abstain=False,
        expected_sources=["alarm_reference.pdf", "maintenance_manual.pdf"],
        focus_entity="A17",
        ground_truth_answer="Alarm A17 indicates hydraulic pressure low (<150 bar). Causes: IV-21 closed/partially closed, low fluid in reservoir, or sensor signal invalid/out of calibration.",
        notes="Conversational framing of Alarm A17 causes."
    ),
    Phase2EvaluationItem(
        id=104,
        category="SEMANTIC_REPHRASED",
        question="Could you clarify the distinction between transducer PS-04 and the newer PS-04A?",
        variation_type="indirect",
        expected_criteria=[
            "not the same",
            "superseded",
            "ecn-1042"
        ],
        expected_abstain=False,
        expected_sources=["ECN-1042.pdf", "component_register.xlsx"],
        focus_entity="PS-04",
        ground_truth_answer="PS-04 and PS-04A are distinct components. PS-04 was the legacy 180 bar sensor, superseded by PS-04A (200 bar, updated signal conditioning circuit) per ECN-1042.",
        notes="Indirect inquiry regarding PS-04 vs PS-04A distinction."
    ),
    Phase2EvaluationItem(
        id=105,
        category="SEMANTIC_REPHRASED",
        question="Which engineering change bulletin authorized replacing pressure sensor PS04 with PS04A?",
        variation_type="abbreviation",
        expected_criteria=[
            "ecn-1042"
        ],
        expected_abstain=False,
        expected_sources=["ECN-1042.pdf", "revision_history.xlsx"],
        focus_entity="PS-04A",
        ground_truth_answer="Engineering Change Notice ECN-1042 authorized replacing PS-04 with PS-04A.",
        notes="Uses compressed tags 'PS04'/'PS04A' and 'engineering change bulletin'."
    ),
    Phase2EvaluationItem(
        id=106,
        category="SEMANTIC_REPHRASED",
        question="Looking at AEG-DWG-H01, what hardware devices have direct purple line control wiring to PLC-03?",
        variation_type="terminology",
        expected_criteria=[
            "ps-04a",
            "iv-21"
        ],
        expected_abstain=False,
        expected_sources=["system_diagram_hydraulic.pdf"],
        focus_entity="PLC-03",
        ground_truth_answer="Direct purple control lines connect PLC-03 to pressure sensor PS-04A and isolation valve IV-21.",
        notes="References drawing ID AEG-DWG-H01 and specifies purple line legend meaning."
    ),
    Phase2EvaluationItem(
        id=107,
        category="SEMANTIC_REPHRASED",
        question="If low pressure warning A17 continues uninterrupted for over 10s, what mandatory shutdown protocol must technicians execute?",
        variation_type="abbreviation",
        expected_criteria=[
            "shutdown procedure 4.7",
            "close iv-21"
        ],
        expected_abstain=False,
        expected_sources=["maintenance_manual.pdf", "alarm_reference.pdf"],
        focus_entity="A17",
        ground_truth_answer="If A17 persists >10 seconds, technicians must execute Shutdown Procedure 4.7: close IV-21, confirm pressure decay, switch power OFF, and tag out.",
        notes="Uses '10s' abbreviation and 'mandatory shutdown protocol' terminology."
    ),
    Phase2EvaluationItem(
        id=108,
        category="SEMANTIC_REPHRASED",
        question="Why is it strictly prohibited to reboot the PLC-03 controller when system hydraulic line pressure exceeds 50 bar?",
        variation_type="conversational",
        expected_criteria=[
            "50 bar",
            "uncommanded"
        ],
        expected_abstain=False,
        expected_sources=["operator_manual.pdf", "maintenance_manual.pdf", "configuration_export.json"],
        focus_entity="PLC-03",
        ground_truth_answer="Resetting above 50 bar is prohibited because re-initializing valve driver outputs under pressure can cause uncommanded transition of isolation valve IV-21.",
        notes="Asks 'why' reboot is prohibited with specific threshold."
    ),
    Phase2EvaluationItem(
        id=109,
        category="SEMANTIC_REPHRASED",
        question="What was the official factory pressure setpoint before software update 3.2, and what engineering document modified it to 200 bar?",
        variation_type="combined_facts",
        expected_criteria=[
            "180 bar",
            "ecn-1042"
        ],
        expected_abstain=False,
        expected_sources=["ECN-1042.pdf", "operator_manual.pdf", "legacy_manual_v1.html"],
        focus_entity="HPU",
        ground_truth_answer="The factory setpoint before rev 3.2 was 180 bar; it was raised to 200 bar by Engineering Change Notice ECN-1042.",
        notes="Combines previous threshold and changing document into a single query."
    ),
    Phase2EvaluationItem(
        id=110,
        category="SEMANTIC_REPHRASED",
        question="Which specific fault code is annunciated when hydraulic pressure drops below 150 bar on Skid A?",
        variation_type="terminology",
        expected_criteria=[
            "a17"
        ],
        expected_abstain=False,
        expected_sources=["alarm_reference.pdf", "configuration_export.json"],
        focus_entity="A17",
        ground_truth_answer="Fault code Alarm A17 (Hydraulic Pressure Low) triggers when pressure drops below 150 bar.",
        notes="Uses 'fault code is annunciated' and location 'Skid A'."
    ),
    Phase2EvaluationItem(
        id=111,
        category="SEMANTIC_REPHRASED",
        question="In which sub-assembly or machine area is isolation valve IV21 physically mounted according to the asset register?",
        variation_type="terminology",
        expected_criteria=[
            "hydraulic module"
        ],
        expected_abstain=False,
        expected_sources=["component_register.xlsx"],
        focus_entity="IV-21",
        ground_truth_answer="Isolation valve IV-21 is located in the 'Hydraulic Module' per the Component Register (AEG-CR-700).",
        notes="Uses 'asset register' and compressed tag 'IV21'."
    ),
    Phase2EvaluationItem(
        id=112,
        category="SEMANTIC_REPHRASED",
        question="Does the operator training slide deck mention any reservoir hardware that is absent from the standard maintenance and operator manuals?",
        variation_type="conversational",
        expected_criteria=[
            "auxiliary reservoir"
        ],
        expected_abstain=False,
        expected_sources=["training_slide_excerpt.pptx"],
        focus_entity="Auxiliary Reservoir",
        ground_truth_answer="Yes, the training slide deck introduces the Auxiliary Reservoir for Line 4/5 peak top-up, which is omitted from the standard manuals.",
        notes="Conversational inquiry regarding slide deck hardware additions."
    ),
    Phase2EvaluationItem(
        id=113,
        category="SEMANTIC_REPHRASED",
        question="What exact physical label string is displayed on the HMI diagnostics panel for the discharge pressure transmitter?",
        variation_type="terminology",
        expected_criteria=[
            "p.s. 04-a",
            "ps-04a"
        ],
        expected_abstain=False,
        expected_sources=["screen_03_diagnostics.png", "component_register.xlsx"],
        focus_entity="PS-04A",
        ground_truth_answer="The HMI diagnostics screen displays 'P.S. 04-A', which represents the physical unit label formatting for PS-04A.",
        notes="Technical phrasing 'exact physical label string' and 'HMI diagnostics panel'."
    ),
    Phase2EvaluationItem(
        id=114,
        category="SEMANTIC_REPHRASED",
        question="On what calendar date was software release 3.2 formally enacted, and what hardware and pressure updates accompanied this release?",
        variation_type="combined_facts",
        expected_criteria=[
            "2025-09-30",
            "ps-04a",
            "200 bar"
        ],
        expected_abstain=False,
        expected_sources=["revision_history.xlsx", "ECN-1042.pdf"],
        focus_entity="Software Revision 3.2",
        ground_truth_answer="Software revision 3.2 took effect on 2025-09-30, replacing PS-04 with PS-04A and raising normal operating pressure to 200 bar.",
        notes="Combines release date, hardware replacement, and pressure adjustment."
    ),
    Phase2EvaluationItem(
        id=115,
        category="SEMANTIC_REPHRASED",
        question="wat is the normal hpu presure setpoint and whitch docuemnt specifies it?",
        variation_type="misspelling",
        expected_criteria=[
            "200 bar",
            "operator_manual.pdf"
        ],
        expected_abstain=False,
        expected_sources=["operator_manual.pdf", "ECN-1042.pdf"],
        focus_entity="HPU",
        ground_truth_answer="Normal HPU pressure setpoint is 200 bar (for rev 3.2+), specified in operator_manual.pdf and ECN-1042.pdf.",
        notes="Intentionally introduces typos: 'wat', 'presure', 'whitch', 'docuemnt'."
    ),

    # =========================================================================
    # CATEGORY 2: Multi-Document Reasoning Questions (10 Questions)
    # =========================================================================
    Phase2EvaluationItem(
        id=201,
        category="MULTI_DOC_REASONING",
        question="Cross-referencing ECN-1042 and component_register.xlsx, why was PS-04 replaced and what is the part number or designation of its replacement?",
        variation_type="cross_doc",
        expected_criteria=[
            "drift",
            "ps-04a",
            "ecn-1042"
        ],
        expected_abstain=False,
        expected_sources=["ECN-1042.pdf", "component_register.xlsx"],
        focus_entity="PS-04",
        ground_truth_answer="ECN-1042 details that PS-04 suffered signal drift after ~18 months triggering nuisance A19 alarms; component_register.xlsx confirms PS-04A as the active replacement part.",
        notes="Synthesizes failure cause from ECN-1042 with component inventory in component_register.xlsx."
    ),
    Phase2EvaluationItem(
        id=202,
        category="MULTI_DOC_REASONING",
        question="Connecting hydraulic schematic AEG-DWG-H01 and electrical drawing AEG-DWG-E02, what electrical voltage powers the controller monitoring IV-21?",
        variation_type="cross_doc",
        expected_criteria=[
            "plc-03",
            "120v",
            "24vdc"
        ],
        expected_abstain=False,
        expected_sources=["system_diagram_hydraulic.pdf", "system_diagram_electrical.png", "component_register.xlsx"],
        focus_entity="PLC-03",
        ground_truth_answer="AEG-DWG-H01 shows PLC-03 controls IV-21; AEG-DWG-E02 and the component register establish control transformer T1 steps 480V down to 120V/24VDC for PLC-03.",
        notes="Synthesizes valve-to-controller mapping from hydraulic schematic with electrical supply specs from electrical drawing."
    ),
    Phase2EvaluationItem(
        id=203,
        category="MULTI_DOC_REASONING",
        question="Comparing operator_manual.pdf Section 4.3 with configuration_export.json, do the 4 mandatory startup interlocks match the JSON parameter keys?",
        variation_type="cross_doc",
        expected_criteria=[
            "valve_iv21_required_state",
            "estop_required_state",
            "maintenance_panel_required_state",
            "fluid_level_required_band"
        ],
        expected_abstain=False,
        expected_sources=["operator_manual.pdf", "configuration_export.json"],
        focus_entity="HPU",
        ground_truth_answer="Yes, the 4 manual preconditions (IV-21 open, E-stop reset, maintenance panel closed, fluid level normal) correspond exactly to startup_interlocks keys in configuration_export.json.",
        notes="Matches procedural manual requirements with JSON configuration keys."
    ),
    Phase2EvaluationItem(
        id=204,
        category="MULTI_DOC_REASONING",
        question="Synthesizing alarm_reference.pdf and maintenance_manual.pdf, what exact shutdown procedure must be initiated if low pressure alarm A17 persists past 10 seconds?",
        variation_type="cross_doc",
        expected_criteria=[
            "procedure 4.7",
            "close iv-21",
            "decay"
        ],
        expected_abstain=False,
        expected_sources=["alarm_reference.pdf", "maintenance_manual.pdf"],
        focus_entity="A17",
        ground_truth_answer="Alarm reference specifies a 10s persistence limit triggering Shutdown Procedure 4.7, which maintenance manual details as closing IV-21, verifying pressure decay, and lockout/tagout.",
        notes="Crosses alarm persistence threshold with maintenance shutdown steps."
    ),
    Phase2EvaluationItem(
        id=205,
        category="MULTI_DOC_REASONING",
        question="Correlating training_slide_excerpt.pptx with AEG-DWG-H01, where is the Auxiliary Reservoir situated and what role does it perform during peak demand?",
        variation_type="cross_doc",
        expected_criteria=[
            "auxiliary reservoir",
            "line 4/5",
            "top-up"
        ],
        expected_abstain=False,
        expected_sources=["training_slide_excerpt.pptx", "system_diagram_hydraulic.pdf"],
        focus_entity="Auxiliary Reservoir",
        ground_truth_answer="Training slides and AEG-DWG-H01 show the Auxiliary Reservoir is connected to Skid B on Lines 4/5 to provide top-up fluid during peak press demand cycles.",
        notes="Cross-references training deck slide 2 with hydraulic schematic topology."
    ),
    Phase2EvaluationItem(
        id=206,
        category="MULTI_DOC_REASONING",
        question="Comparing revision_history.xlsx and ECN-1042, confirm whether the software 3.2 effective date matches the enactment of the 200 bar operating pressure threshold.",
        variation_type="cross_doc",
        expected_criteria=[
            "2025-09-30",
            "revision 3.2",
            "200 bar"
        ],
        expected_abstain=False,
        expected_sources=["revision_history.xlsx", "ECN-1042.pdf"],
        focus_entity="Software Revision 3.2",
        ground_truth_answer="Yes, both revision_history.xlsx and ECN-1042 confirm software revision 3.2 took effect on 2025-09-30, enacting the 200 bar setpoint and PS-04A sensor.",
        notes="Verifies date and threshold alignment between changelog and engineering bulletin."
    ),
    Phase2EvaluationItem(
        id=207,
        category="MULTI_DOC_REASONING",
        question="Cross-referencing scanned_appendix_calibration.pdf and wiring_diagram.pdf, what signaling standard (e.g. 4-20mA) and terminal block are used by pressure sensor PS-04A?",
        variation_type="cross_doc",
        expected_criteria=[
            "4-20ma",
            "tb-7"
        ],
        expected_abstain=False,
        expected_sources=["scanned_appendix_calibration.pdf", "wiring_diagram.pdf", "component_register.xlsx"],
        focus_entity="PS-04A",
        ground_truth_answer="Calibration records and wiring diagram AEG-DWG-W03 confirm PS-04A uses a 4-20mA current loop wired to Terminal Block TB-7.",
        notes="Combines calibration signal type with physical wiring drawing terminal block designation."
    ),
    Phase2EvaluationItem(
        id=208,
        category="MULTI_DOC_REASONING",
        question="Comparing legacy_manual_v1.html with operator_manual.pdf Rev 4, what operating pressure and sensor changes distinguish the legacy system from the active system?",
        variation_type="cross_doc",
        expected_criteria=[
            "180 bar",
            "200 bar",
            "ps-04",
            "ps-04a"
        ],
        expected_abstain=False,
        expected_sources=["legacy_manual_v1.html", "operator_manual.pdf", "ECN-1042.pdf"],
        focus_entity="HPU",
        ground_truth_answer="Legacy manual v1 specifies 180 bar operating pressure using sensor PS-04, whereas Rev 4 specifies 200 bar operating pressure using sensor PS-04A.",
        notes="Compares superseded v1 HTML manual with current active Rev 4 PDF manual."
    ),
    Phase2EvaluationItem(
        id=209,
        category="MULTI_DOC_REASONING",
        question="Evaluating site_survey_notes.docx against ECN-1042, why does the 175 bar reading recorded on Line 4 not invalidate the official 200 bar setpoint?",
        variation_type="cross_doc",
        expected_criteria=[
            "175 bar",
            "uncalibrated",
            "field"
        ],
        expected_abstain=False,
        expected_sources=["site_survey_notes.docx", "ECN-1042.pdf", "operator_manual.pdf"],
        focus_entity="HPU",
        ground_truth_answer="The 175 bar observation in site survey notes was taken on an uncalibrated local Line 4 gauge and has unreviewed field trust (0.35), so it cannot supersede authoritative ECN-1042 (1.0).",
        notes="Requires conflict reconciliation reasoning between low-trust field notes and authoritative bulletin."
    ),
    Phase2EvaluationItem(
        id=210,
        category="MULTI_DOC_REASONING",
        question="Reconciling ECN-1058 and alarm_reference.pdf, how is Alarm A17 evaluated on machines with older firmware vs firmware 3.2?",
        variation_type="cross_doc",
        expected_criteria=[
            "ps-04",
            "ps-04a",
            "150 bar"
        ],
        expected_abstain=False,
        expected_sources=["ECN-1058.pdf", "alarm_reference.pdf"],
        focus_entity="A17",
        ground_truth_answer="ECN-1058 clarifies that Alarm A17 (<150 bar) evaluates against whichever sensor is active for the unit's firmware: PS-04 on pre-3.2 units, and PS-04A on post-3.2 units.",
        notes="Synthesizes ECN-1058 cross-firmware alarm evaluation clarification with Alarm A17 threshold."
    ),

    # =========================================================================
    # CATEGORY 3: Entity Disambiguation Questions (5 Questions)
    # =========================================================================
    Phase2EvaluationItem(
        id=301,
        category="ENTITY_DISAMBIGUATION",
        question="Are sensor PS-04 on Skid A and sensor PS-40 on Skid B interchangeable or related to each other?",
        variation_type="conversational",
        expected_criteria=[
            "not the same",
            "coolant loop",
            "skid b"
        ],
        expected_abstain=False,
        expected_sources=["component_register.xlsx", "configuration_export.json"],
        focus_entity="PS-40",
        ground_truth_answer="No, PS-04 and PS-40 are completely separate components. PS-04 was the HPU discharge sensor on Skid A; PS-40 monitors the Coolant Loop on Skid B. They must never be merged.",
        notes="Disambiguates PS-04 from PS-40 across different skids and loops."
    ),
    Phase2EvaluationItem(
        id=302,
        category="ENTITY_DISAMBIGUATION",
        question="Explain why pressure transmitter PS-04 cannot be directly swapped for PS-04A without a controller firmware check.",
        variation_type="terminology",
        expected_criteria=[
            "not the same",
            "firmware 3.2",
            "circuit"
        ],
        expected_abstain=False,
        expected_sources=["ECN-1042.pdf", "component_register.xlsx"],
        focus_entity="PS-04A",
        ground_truth_answer="PS-04A is not a form-fit-function equivalent to PS-04. It has updated signal conditioning circuitry and strictly requires controller firmware revision 3.2 or later.",
        notes="Distinguishes form-fit-function limitations between PS-04 and PS-04A."
    ),
    Phase2EvaluationItem(
        id=303,
        category="ENTITY_DISAMBIGUATION",
        question="Is the device designated 'P.S. 04-A' on the HMI diagnostics screen an unlisted third sensor or does it map to an existing registered asset?",
        variation_type="indirect",
        expected_criteria=[
            "matches",
            "ps-04a",
            "physical label"
        ],
        expected_abstain=False,
        expected_sources=["screen_03_diagnostics.png", "component_register.xlsx"],
        focus_entity="PS-04A",
        ground_truth_answer="'P.S. 04-A' is not a third sensor; it is the physical unit silkscreen label formatting for canonical component PS-04A, confirmed by the diagnostics screen note.",
        notes="Disambiguates label formatting variation 'P.S. 04-A' from canonical PS-04A."
    ),
    Phase2EvaluationItem(
        id=304,
        category="ENTITY_DISAMBIGUATION",
        question="How does the Main Reservoir on Skid A differ in operational role and documentation coverage from the Auxiliary Reservoir on Skid B?",
        variation_type="terminology",
        expected_criteria=[
            "main reservoir",
            "auxiliary reservoir",
            "line 4/5"
        ],
        expected_abstain=False,
        expected_sources=["operator_manual.pdf", "training_slide_excerpt.pptx"],
        focus_entity="Main Reservoir",
        ground_truth_answer="Main Reservoir is standard equipment on Skid A covered in all manuals; Auxiliary Reservoir is a Line 4/5-specific peak demand top-up tank omitted from standard manuals.",
        notes="Disambiguates Main Reservoir vs Auxiliary Reservoir roles and documentation coverage."
    ),
    Phase2EvaluationItem(
        id=305,
        category="ENTITY_DISAMBIGUATION",
        question="In Control Cabinet 1, how do the functions and voltage domains of incoming disconnect Q1 and control transformer T1 differ?",
        variation_type="terminology",
        expected_criteria=[
            "q1",
            "t1",
            "480v",
            "120v"
        ],
        expected_abstain=False,
        expected_sources=["system_diagram_electrical.png", "component_register.xlsx"],
        focus_entity="Q1",
        ground_truth_answer="Q1 is the incoming 480V 3-phase main disconnect switch; T1 is the control transformer stepping 480V down to 120V for internal control circuits.",
        notes="Disambiguates electrical power devices Q1 and T1 in Control Cabinet 1."
    ),

    # =========================================================================
    # CATEGORY 4: False-Premise Questions (5 Questions)
    # =========================================================================
    Phase2EvaluationItem(
        id=401,
        category="FALSE_PREMISE",
        question="Why was the operating pressure for sensor PS-04 set to 200 bar on legacy firmware 3.0?",
        variation_type="false_assumption",
        expected_criteria=[
            "false premise",
            "180 bar",
            "not 200 bar"
        ],
        expected_abstain=False,
        is_false_premise=True,
        expected_sources=["ECN-1042.pdf", "legacy_manual_v1.html", "configuration_export.json"],
        focus_entity="PS-04",
        ground_truth_answer="The premise is false: sensor PS-04 on legacy firmware 3.0 operated at 180 bar, not 200 bar. The 200 bar threshold applies only to firmware >=3.2 with sensor PS-04A.",
        notes="False premise: conflates PS-04 with 200 bar on firmware 3.0."
    ),
    Phase2EvaluationItem(
        id=402,
        category="FALSE_PREMISE",
        question="What is the recommended maintenance procedure for the pressure sensor PS-40 installed on the HPU discharge line?",
        variation_type="false_assumption",
        expected_criteria=[
            "false premise",
            "not on hpu",
            "coolant loop",
            "skid b"
        ],
        expected_abstain=False,
        is_false_premise=True,
        expected_sources=["component_register.xlsx", "configuration_export.json"],
        focus_entity="PS-40",
        ground_truth_answer="The premise is false: sensor PS-40 is not installed on the HPU discharge line. PS-40 is located on Skid B in the Coolant Loop; the HPU discharge line uses PS-04 / PS-04A.",
        notes="False premise: assumes PS-40 is on HPU discharge line."
    ),
    Phase2EvaluationItem(
        id=403,
        category="FALSE_PREMISE",
        question="According to electrical drawing AEG-DWG-E02, what is the required recalibration frequency for the voltage sensor?",
        variation_type="false_assumption",
        expected_criteria=[
            "false premise",
            "no voltage sensor",
            "not specified"
        ],
        expected_abstain=True,
        is_false_premise=True,
        expected_sources=["system_diagram_electrical.png", "scanned_appendix_calibration.pdf"],
        focus_entity="Electrical System Diagram",
        ground_truth_answer="The question contains a false premise: electrical drawing AEG-DWG-E02 contains no voltage sensor, and calibration intervals are explicitly omitted from the documentation.",
        notes="False premise: assumes a voltage sensor exists on AEG-DWG-E02."
    ),
    Phase2EvaluationItem(
        id=404,
        category="FALSE_PREMISE",
        question="Under what conditions is an operator permitted to reset controller PLC-03 while system pressure is at 100 bar?",
        variation_type="false_assumption",
        expected_criteria=[
            "prohibited",
            "50 bar",
            "never"
        ],
        expected_abstain=False,
        is_false_premise=True,
        expected_sources=["operator_manual.pdf", "maintenance_manual.pdf", "configuration_export.json"],
        focus_entity="PLC-03",
        ground_truth_answer="The premise is false: an operator is NEVER permitted to reset PLC-03 at 100 bar. Firmware strictly blocks reset above 50 bar to prevent uncommanded valve transition.",
        notes="False premise: assumes reset might be permissible at 100 bar."
    ),
    Phase2EvaluationItem(
        id=405,
        category="FALSE_PREMISE",
        question="Which engineering director signed the formal approval section of engineering change notice ECN-1058?",
        variation_type="false_assumption",
        expected_criteria=[
            "not specified",
            "no approval block",
            "not signed"
        ],
        expected_abstain=True,
        is_false_premise=True,
        expected_sources=["ECN-1058.pdf"],
        focus_entity="ECN-1058",
        ground_truth_answer="The question contains a false premise: ECN-1058 omits author, approver, and signature blocks entirely despite having Released status.",
        notes="False premise: assumes ECN-1058 has an approval signature block."
    ),

    # =========================================================================
    # CATEGORY 5: Unanswerable Questions Requiring Abstention (5 Questions)
    # =========================================================================
    Phase2EvaluationItem(
        id=501,
        category="UNANSWERABLE_ABSTENTION",
        question="What is the maximum continuous ambient operating temperature specification for pressure sensor PS-04A?",
        variation_type="indirect",
        expected_criteria=[
            "not specified",
            "not documented"
        ],
        expected_abstain=True,
        is_false_premise=False,
        expected_sources=["All Package Documents"],
        focus_entity="PS-04A",
        ground_truth_answer="The documentation package does not specify the maximum continuous operating temperature for PS-04A. System must abstain.",
        notes="Unanswerable: thermal specifications are absent from package."
    ),
    Phase2EvaluationItem(
        id=502,
        category="UNANSWERABLE_ABSTENTION",
        question="What is the mean time between failures (MTBF) in operating hours for isolation valve IV-21?",
        variation_type="terminology",
        expected_criteria=[
            "not specified",
            "not documented"
        ],
        expected_abstain=True,
        is_false_premise=False,
        expected_sources=["All Package Documents"],
        focus_entity="IV-21",
        ground_truth_answer="The documentation package does not provide MTBF reliability ratings for isolation valve IV-21. System must abstain.",
        notes="Unanswerable: reliability MTBF metrics are absent from package."
    ),
    Phase2EvaluationItem(
        id=503,
        category="UNANSWERABLE_ABSTENTION",
        question="Can the Aegis Series-7 HCS electrical enclosure be connected directly to a 400V 3-phase European mains supply without a step-up transformer?",
        variation_type="conversational",
        expected_criteria=[
            "not documented",
            "480v"
        ],
        expected_abstain=True,
        is_false_premise=False,
        expected_sources=["component_register.xlsx", "system_diagram_electrical.png"],
        focus_entity="Aegis Series-7 HCS",
        ground_truth_answer="The documentation does not support 400V 3-phase compatibility; all specifications require a 480V supply. System must abstain.",
        notes="Unanswerable: 400V compatibility is unsupported in package."
    ),
    Phase2EvaluationItem(
        id=504,
        category="UNANSWERABLE_ABSTENTION",
        question="What is the acoustic noise emission level in dBA of the HPU pump motor when running at full 200 bar continuous load?",
        variation_type="terminology",
        expected_criteria=[
            "not specified",
            "not documented"
        ],
        expected_abstain=True,
        is_false_premise=False,
        expected_sources=["All Package Documents"],
        focus_entity="HPU",
        ground_truth_answer="The documentation package does not contain acoustic noise (dBA) ratings for the HPU pump motor. System must abstain.",
        notes="Unanswerable: acoustic noise ratings are absent from package."
    ),
    Phase2EvaluationItem(
        id=505,
        category="UNANSWERABLE_ABSTENTION",
        question="What is the dynamic viscosity of the hydraulic fluid at 120 degrees Celsius according to the system documentation?",
        variation_type="terminology",
        expected_criteria=[
            "not specified",
            "not documented"
        ],
        expected_abstain=True,
        is_false_premise=False,
        expected_sources=["All Package Documents"],
        focus_entity="Hydraulic Fluid",
        ground_truth_answer="The system documentation and MSDS do not provide hydraulic fluid viscosity at 120°C. System must abstain.",
        notes="Unanswerable: high-temperature fluid viscosity curve is absent."
    ),

    # =========================================================================
    # CATEGORY 6: Targeted Adversarial Scenarios (5 Questions)
    # =========================================================================
    Phase2EvaluationItem(
        id=601,
        category="ADVERSARIAL",
        question="If a maintenance technician replaces a broken PS-04 with a new PS-04A on a press running firmware 3.1, will it function properly at 200 bar?",
        variation_type="adversarial_scoping",
        expected_criteria=[
            "firmware 3.2",
            "cannot",
            "not compatible"
        ],
        expected_abstain=False,
        expected_sources=["ECN-1042.pdf", "operator_manual.pdf"],
        focus_entity="PS-04A",
        ground_truth_answer="No. PS-04A strictly requires controller firmware 3.2 or later and is not a plug-and-play replacement on firmware 3.1. Firmware 3.1 operates at 180 bar.",
        notes="Adversarial: tests applying 200 bar and PS-04A to older firmware."
    ),
    Phase2EvaluationItem(
        id=602,
        category="ADVERSARIAL",
        question="Can we route the coolant line pressure readings from PS-40 into the HPU A17 alarm logic?",
        variation_type="adversarial_scoping",
        expected_criteria=[
            "unrelated",
            "coolant loop",
            "do not map"
        ],
        expected_abstain=False,
        expected_sources=["configuration_export.json", "component_register.xlsx"],
        focus_entity="PS-40",
        ground_truth_answer="No. Configuration explicitly warns that PS-40 is in the Skid B Coolant Loop, completely unrelated to HPU discharge circuit, and must never be mapped to sensor_ps04a_* or A17.",
        notes="Adversarial: tests confusing PS-40 with PS-04/PS-04A in alarm logic."
    ),
    Phase2EvaluationItem(
        id=603,
        category="ADVERSARIAL",
        question="Given that the plant operates on a 400V 3-phase grid, how should transformer T1 be re-tapped according to the electrical documentation?",
        variation_type="adversarial_scoping",
        expected_criteria=[
            "not documented",
            "480v",
            "no 400v tap"
        ],
        expected_abstain=True,
        expected_sources=["system_diagram_electrical.png", "component_register.xlsx"],
        focus_entity="T1",
        ground_truth_answer="The documentation does not document 400V re-tapping; T1 is specified strictly as 480:120V with no 400V taps documented. System must abstain or reject assumption.",
        notes="Adversarial: attempts to force 400V re-tapping assumption onto 480:120V transformer."
    ),
    Phase2EvaluationItem(
        id=604,
        category="ADVERSARIAL",
        question="Is it safe to operate pressure sensor PS-04A continuously at 95°C based on the published thermal rating in the manual?",
        variation_type="adversarial_scoping",
        expected_criteria=[
            "not specified",
            "no published thermal rating"
        ],
        expected_abstain=True,
        expected_sources=["All Package Documents"],
        focus_entity="PS-04A",
        ground_truth_answer="The documentation contains no published thermal rating or temperature limit for PS-04A. System must abstain rather than affirming 95°C operation.",
        notes="Adversarial: treats an undocumented temperature as a known published rating."
    ),
    Phase2EvaluationItem(
        id=605,
        category="ADVERSARIAL",
        question="Does drawing line 7 in hydraulic schematic AEG-DWG-H01 prove that hydraulic oil flows into PLC-03 during normal operation?",
        variation_type="adversarial_scoping",
        expected_criteria=[
            "uncertain edge",
            "review",
            "electronic controller"
        ],
        expected_abstain=False,
        expected_sources=["system_diagram_hydraulic.pdf"],
        focus_entity="PLC-03",
        ground_truth_answer="No. While drawing line 7 is grey (fluid line) connecting PLC-03 to HPU, electronic controllers do not carry hydraulic fluid; this is an anomalous edge flagged for review.",
        notes="Adversarial: tests hydraulic schematic topological anomaly / uncertain edge."
    )
]

