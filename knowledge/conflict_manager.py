"""
Conflict and Revision Management Engine for the Aegis Knowledge Intelligence System.
Maintains revision-scoped facts, source reliability ranking, and historical preservation.
Prevents silent overwrites while reconciling divergent documentation claims.
"""

from typing import List, Dict, Any, Optional
from storage.models import Conflict, Fact


# Standard reliability tiers
TRUST_WEIGHTS = {
    "AUTHORITATIVE_BULLETIN": 1.0,  # ECNs supersede all older manuals
    "SYSTEM_CONFIG": 0.95,          # Controller firmware dumps
    "OFFICIAL": 0.95,               # Current active manuals and registers
    "VERIFIED_RECORD": 0.80,        # Signed calibration forms, live HMI captures
    "OFFICIAL_SUPERSEDED": 0.60,    # Legacy v1 manual exports
    "FIELD_UNREVIEWED": 0.35,       # Unverified notebook field notes
    "NOISE": 0.10                   # Out-of-domain / MSDS sheets
}


class ConflictManager:
    """Detects, analyzes, and explicitly resolves version-scoped and inter-document conflicts."""

    def __init__(self):
        self.conflicts: List[Conflict] = []
        self._init_standard_conflicts()

    def _init_standard_conflicts(self):
        """Pre-define the core known conflicts in the Aegis Series-7 package."""
        
        # Conflict 1: Operating Pressure Setpoint (180 bar vs 200 bar vs 175 bar)
        self.conflicts.append(Conflict(
            conflict_id="CONF-001",
            topic="HPU Normal Operating Pressure Setpoint",
            entity_id="HPU",
            conflicting_facts=[
                {
                    "source": "manuals/operator_manual.pdf (Rev 4, Sec 4.3, 5)",
                    "value": "200 bar",
                    "applicability": "Software revision 3.2 and later (units manufactured after 2024)",
                    "trust_level": "OFFICIAL",
                    "status": "CURRENT_ACTIVE"
                },
                {
                    "source": "engineering_bulletins/ECN-1042.pdf (Sec 1)",
                    "value": "200 bar (revised from 180 bar)",
                    "applicability": "Effective software revision 3.2",
                    "trust_level": "AUTHORITATIVE_BULLETIN",
                    "status": "CURRENT_ACTIVE"
                },
                {
                    "source": "configuration/configuration_export.json (sensor_ps04a_threshold_bar)",
                    "value": "200 bar",
                    "applicability": "Firmware 3.2.1",
                    "trust_level": "SYSTEM_CONFIG",
                    "status": "CURRENT_ACTIVE"
                },
                {
                    "source": "manuals/legacy_manual_v1.html (Sec 5)",
                    "value": "180 bar",
                    "applicability": "Software revisions 3.0 and 3.1 only",
                    "trust_level": "OFFICIAL_SUPERSEDED",
                    "status": "HISTORICAL_SUPERSEDED"
                },
                {
                    "source": "configuration/configuration_export.json (sensor_ps04_legacy_threshold_bar)",
                    "value": "180 bar",
                    "applicability": "Applies before firmware 3.2",
                    "trust_level": "SYSTEM_CONFIG",
                    "status": "HISTORICAL_SUPERSEDED"
                },
                {
                    "source": "low_trust/site_survey_notes.docx (Line 4 HPU notes)",
                    "value": "175 bar (local gauge observation)",
                    "applicability": "Line 4 field visit (uncalibrated gauge)",
                    "trust_level": "FIELD_UNREVIEWED",
                    "status": "REJECTED_AS_SPECIFICATION"
                }
            ],
            resolution_status="VERSION_SCOPED",
            resolution_rationale=(
                "The 180 bar and 200 bar specifications are version-scoped, not mutually exclusive errors. "
                "Per ECN-1042 and Operator Manual Rev 4, 180 bar was the standard setpoint for software revisions < 3.2. "
                "Effective software revision 3.2, the setpoint was increased to 200 bar to improve cycle times. "
                "The 175 bar reading in site_survey_notes.docx represents an unverified field observation on an uncalibrated local gauge, "
                "and does not alter the official engineering setpoint."
            ),
            preferred_fact_id="fact_hpu_operating_pressure_current"
        ))

        # Conflict 2: Pressure Sensor Supersession (PS-04 vs PS-04A)
        self.conflicts.append(Conflict(
            conflict_id="CONF-002",
            topic="HPU Discharge Pressure Sensor Active Model",
            entity_id="PS-04A",
            conflicting_facts=[
                {
                    "source": "manuals/legacy_manual_v1.html & component_register.xlsx",
                    "value": "PS-04",
                    "applicability": "Software revision < 3.2",
                    "trust_level": "OFFICIAL_SUPERSEDED",
                    "status": "SUPERSEDED"
                },
                {
                    "source": "engineering_bulletins/ECN-1042.pdf",
                    "value": "PS-04A",
                    "applicability": "Software revision >= 3.2",
                    "trust_level": "AUTHORITATIVE_BULLETIN",
                    "status": "CURRENT_ACTIVE"
                }
            ],
            resolution_status="SUPERSEDED_BY_ECN",
            resolution_rationale=(
                "ECN-1042 explicitly supersedes PS-04 with PS-04A for all units at software revision 3.2 or later. "
                "PS-04 remains installed only on units running legacy firmware."
            ),
            preferred_fact_id="fact_ps04a_active"
        ))

        # Conflict 3: Alarm A17 Evaluation Sensor Reference
        self.conflicts.append(Conflict(
            conflict_id="CONF-003",
            topic="Alarm A17 Sensor Reference Condition",
            entity_id="A17",
            conflicting_facts=[
                {
                    "source": "reference/alarm_reference.pdf (pre-Rev 5 text)",
                    "value": "Evaluated specifically against sensor PS-04",
                    "trust_level": "OFFICIAL_SUPERSEDED",
                    "status": "SUPERSEDED"
                },
                {
                    "source": "engineering_bulletins/ECN-1058.pdf & alarm_reference.pdf Rev 5",
                    "value": "Evaluated against whichever sensor is active for installed revision (PS-04 or PS-04A)",
                    "trust_level": "AUTHORITATIVE_BULLETIN",
                    "status": "CURRENT_ACTIVE"
                }
            ],
            resolution_status="SUPERSEDED_BY_ECN",
            resolution_rationale=(
                "ECN-1058 issued a documentation correction establishing that Alarm A17's condition evaluates against the active sensor "
                "(PS-04 pre-3.2, PS-04A post-3.2). The low-pressure threshold itself remains constant at 150 bar."
            ),
            preferred_fact_id="fact_a17_sensor_condition_ecn1058"
        ))

        # Conflict 4: Diagram Connection Anomaly (PLC-03 to HPU)
        self.conflicts.append(Conflict(
            conflict_id="CONF-004",
            topic="Hydraulic Schematic Line Anomaly: PLC-03 to HPU",
            entity_id="PLC-03",
            conflicting_facts=[
                {
                    "source": "diagrams/system_diagram_hydraulic.pdf (Line 7)",
                    "value": "Grey line (Hydraulic fluid path) connects PLC-03 to HPU",
                    "trust_level": "OFFICIAL",
                    "status": "FLAGGED_ANOMALY"
                },
                {
                    "source": "diagrams/system_diagram_hydraulic.pdf (Legend & Lines 8, 9)",
                    "value": "Purple lines (Control/signal connections) connect PLC-03 to PS-04A and IV-21",
                    "trust_level": "OFFICIAL",
                    "status": "VERIFIED_SIGNAL_LOOP"
                }
            ],
            resolution_status="UNRESOLVED",
            resolution_rationale=(
                "The purple signal lines between PLC-03 and PS-04A/IV-21 are structurally confirmed. "
                "The grey line connecting PLC-03 to HPU contradicts hydraulic design principles (electronic controllers do not carry fluid). "
                "Status is explicitly preserved as UNCERTAIN_EDGE_FLAGGED_FOR_REVIEW for manual engineering inspection."
            ),
            preferred_fact_id=None
        ))

    def get_all_conflicts(self) -> List[Conflict]:
        return self.conflicts

    def get_conflict_for_topic(self, topic_sub: str) -> Optional[Conflict]:
        for c in self.conflicts:
            if topic_sub.lower() in c.topic.lower() or (c.entity_id and topic_sub.lower() in c.entity_id.lower()):
                return c
        return None

