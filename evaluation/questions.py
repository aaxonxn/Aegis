"""
Ground Truth Benchmark Specification for the 23 Evaluation Questions.
Extracted from evaluation-questions.pdf with explicit criteria, expected sources, and abstention markers.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class EvaluationItem(BaseModel):
    id: int
    question: str
    expected_criteria: List[str]
    expected_abstain: bool
    expected_sources: List[str]
    focus_entity: str
    notes: str = ""


EVALUATION_QUESTIONS_SPEC: List[EvaluationItem] = [
    EvaluationItem(
        id=1,
        question="What must be true before starting the Hydraulic Power Unit?",
        expected_criteria=[
            "fluid level normal",
            "iv-21 open",
            "emergency stop reset",
            "maintenance panel closed"
        ],
        expected_abstain=False,
        expected_sources=["operator_manual.pdf", "configuration_export.json", "screen_01_home.png"],
        focus_entity="HPU",
        notes="All 4 startup interlocks must be verified before start."
    ),
    EvaluationItem(
        id=2,
        question="What is the current normal operating pressure for the HPU, and under what conditions does that apply?",
        expected_criteria=[
            "200 bar",
            "software revision 3.2"
        ],
        expected_abstain=False,
        expected_sources=["operator_manual.pdf", "ECN-1042.pdf", "configuration_export.json"],
        focus_entity="HPU",
        notes="200 bar setpoint applies to firmware >= 3.2; earlier revisions operated at 180 bar."
    ),
    EvaluationItem(
        id=3,
        question="What does alarm A17 indicate, and what are its possible causes?",
        expected_criteria=[
            "low hydraulic pressure",
            "iv-21 closed",
            "low fluid",
            "sensor invalid"
        ],
        expected_abstain=False,
        expected_sources=["alarm_reference.pdf", "maintenance_manual.pdf"],
        focus_entity="A17",
        notes="Pressure < 150 bar. Three primary causes listed in Alarm Reference."
    ),
    EvaluationItem(
        id=4,
        question="Is PS-04 the same component as PS-04A?",
        expected_criteria=[
            "not the same",
            "superseded",
            "ecn-1042"
        ],
        expected_abstain=False,
        expected_sources=["ECN-1042.pdf", "component_register.xlsx"],
        focus_entity="PS-04",
        notes="PS-04 superseded by PS-04A due to signal drift after 18 months."
    ),
    EvaluationItem(
        id=5,
        question="Which document introduced the change from PS-04 to PS-04A?",
        expected_criteria=[
            "ecn-1042"
        ],
        expected_abstain=False,
        expected_sources=["ECN-1042.pdf", "revision_history.xlsx"],
        focus_entity="PS-04A",
        notes="Engineering Change Notice ECN-1042 enacted effective software revision 3.2."
    ),
    EvaluationItem(
        id=6,
        question="Which components connect directly to the HCS controller, according to the hydraulic schematic?",
        expected_criteria=[
            "ps-04a",
            "iv-21",
            "purple",
            "grey line"
        ],
        expected_abstain=False,
        expected_sources=["system_diagram_hydraulic.pdf"],
        focus_entity="PLC-03",
        notes="Purple control lines connect directly to PS-04A and IV-21. Grey fluid line to HPU is an uncertain edge for manual review."
    ),
    EvaluationItem(
        id=7,
        question="What action is required if alarm A17 persists for more than 10 seconds?",
        expected_criteria=[
            "shutdown procedure 4.7",
            "close iv-21"
        ],
        expected_abstain=False,
        expected_sources=["maintenance_manual.pdf", "alarm_reference.pdf", "configuration_export.json"],
        focus_entity="A17",
        notes="Execute Procedure 4.7; silencing alarm alone is prohibited."
    ),
    EvaluationItem(
        id=8,
        question="Under what circumstances must the controller not be reset?",
        expected_criteria=[
            "50 bar",
            "uncommanded"
        ],
        expected_abstain=False,
        expected_sources=["operator_manual.pdf", "maintenance_manual.pdf", "configuration_export.json"],
        focus_entity="PLC-03",
        notes="Must not reset when pressure is > 50 bar to prevent uncommanded valve transition."
    ),
    EvaluationItem(
        id=9,
        question="What was the operating pressure threshold before software revision 3.2, and what changed it?",
        expected_criteria=[
            "180 bar",
            "ecn-1042"
        ],
        expected_abstain=False,
        expected_sources=["ECN-1042.pdf", "operator_manual.pdf", "legacy_manual_v1.html", "configuration_export.json"],
        focus_entity="HPU",
        notes="Was 180 bar; changed to 200 bar by ECN-1042."
    ),
    EvaluationItem(
        id=10,
        question="Which alarm is associated with a pressure sensor reading below 150 bar?",
        expected_criteria=[
            "a17"
        ],
        expected_abstain=False,
        expected_sources=["alarm_reference.pdf", "configuration_export.json"],
        focus_entity="A17",
        notes="Alarm A17 (Hydraulic Pressure Low)."
    ),
    EvaluationItem(
        id=11,
        question="According to the component register, what is the location of the isolation valve IV-21?",
        expected_criteria=[
            "hydraulic module"
        ],
        expected_abstain=False,
        expected_sources=["component_register.xlsx"],
        focus_entity="IV-21",
        notes="Location listed verbatim as 'Hydraulic Module' in AEG-CR-700."
    ),
    EvaluationItem(
        id=12,
        question="Does the training slide deck introduce any component or alarm not found in the manuals?",
        expected_criteria=[
            "auxiliary reservoir",
            "not introduce"
        ],
        expected_abstain=False,
        expected_sources=["training_slide_excerpt.pptx"],
        focus_entity="Auxiliary Reservoir",
        notes="Introduces Auxiliary Reservoir for Line 4/5 peak demand top-up."
    ),
    EvaluationItem(
        id=13,
        question="What sensor ID appears on the diagnostics screenshot, and does it match a known component?",
        expected_criteria=[
            "p.s. 04-a",
            "ps-04a"
        ],
        expected_abstain=False,
        expected_sources=["screen_03_diagnostics.png", "component_register.xlsx"],
        focus_entity="PS-04A",
        notes="Displays 'P.S. 04-A', which matches PS-04A per on-screen physical label note."
    ),
    EvaluationItem(
        id=14,
        question="Per the revision history, when did software revision 3.2 take effect, and what changed alongside it?",
        expected_criteria=[
            "2025-09-30",
            "ps-04a",
            "200 bar"
        ],
        expected_abstain=False,
        expected_sources=["revision_history.xlsx", "ECN-1042.pdf"],
        focus_entity="Software Revision 3.2",
        notes="Took effect 2025-09-30. Replaced PS-04 with PS-04A, changed setpoint to 200 bar."
    ),
    EvaluationItem(
        id=15,
        question="What does sensor_ps04a_threshold_bar in the configuration export correspond to in the operator manual's terminology?",
        expected_criteria=[
            "normal operating pressure"
        ],
        expected_abstain=False,
        expected_sources=["configuration_export.json", "operator_manual.pdf"],
        focus_entity="PS-04A",
        notes="Corresponds to 'normal operating pressure' / setpoint (200 bar)."
    ),
    EvaluationItem(
        id=16,
        question="Does the 200 bar threshold apply to all Aegis HCS units, or only some?",
        expected_criteria=[
            "only some",
            "revision 3.2"
        ],
        expected_abstain=False,
        expected_sources=["ECN-1042.pdf", "operator_manual.pdf", "configuration_export.json"],
        focus_entity="HPU",
        notes="Only units running revision >= 3.2 with PS-04A installed."
    ),
    EvaluationItem(
        id=17,
        question="Is PS-04 the same as PS-40?",
        expected_criteria=[
            "not the same",
            "coolant loop"
        ],
        expected_abstain=False,
        expected_sources=["component_register.xlsx", "configuration_export.json"],
        focus_entity="PS-40",
        notes="Completely separate components: PS-04 on Skid A HPU; PS-40 on Skid B Coolant Loop."
    ),
    EvaluationItem(
        id=18,
        question="What was the pressure limit before revision 3.2?",
        expected_criteria=[
            "180 bar"
        ],
        expected_abstain=False,
        expected_sources=["ECN-1042.pdf", "operator_manual.pdf", "legacy_manual_v1.html", "configuration_export.json"],
        focus_entity="HPU",
        notes="Normal operating pressure setpoint was 180 bar prior to rev 3.2."
    ),
    EvaluationItem(
        id=19,
        question="What is the maximum continuous operating temperature of PS-04A?",
        expected_criteria=[
            "not specified",
            "not documented"
        ],
        expected_abstain=True,
        expected_sources=["All Package Documents"],
        focus_entity="PS-04A",
        notes="UNANSWERABLE: Thermal operating limits are absent from the package. System must abstain."
    ),
    EvaluationItem(
        id=20,
        question="What is the calibration interval for the electrical system diagram's voltage sensor?",
        expected_criteria=[
            "not specified",
            "no voltage sensor"
        ],
        expected_abstain=True,
        expected_sources=["system_diagram_electrical.png", "scanned_appendix_calibration.pdf"],
        focus_entity="Electrical System Diagram",
        notes="UNANSWERABLE / FALSE PREMISE: Electrical drawing has no voltage sensor; calibration interval is omitted."
    ),
    EvaluationItem(
        id=21,
        question="Who approved engineering bulletin ECN-1058?",
        expected_criteria=[
            "not specified",
            "not documented"
        ],
        expected_abstain=True,
        expected_sources=["ECN-1058.pdf"],
        focus_entity="ECN-1058",
        notes="UNANSWERABLE: ECN-1058 has status Released but omits approver/author identity."
    ),
    EvaluationItem(
        id=22,
        question="What is the mean time between failures for the isolation valve IV-21?",
        expected_criteria=[
            "not specified",
            "not documented"
        ],
        expected_abstain=True,
        expected_sources=["All Package Documents"],
        focus_entity="IV-21",
        notes="UNANSWERABLE: MTBF reliability figures for IV-21 are absent from documentation."
    ),
    EvaluationItem(
        id=23,
        question="Is the Aegis Series-7 HCS compatible with a 3-phase 400V supply?",
        expected_criteria=[
            "not documented",
            "480v"
        ],
        expected_abstain=True,
        expected_sources=["component_register.xlsx", "system_diagram_electrical.png"],
        focus_entity="Aegis Series-7 HCS",
        notes="UNANSWERABLE / UNSUPPORTED: System specifies 480V supply; 400V compatibility is unsupported in docs."
    )
]
