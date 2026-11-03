"""
Entity Resolution and Disambiguation Engine for Aegis Knowledge Intelligence System.
Implements canonical ID mapping, strict alias normalization, and non-obvious decision logging.
Explicitly forbids merging similar names (e.g., PS-04, PS-04A, PS-40).
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from storage.models import Entity


# Curated, authoritative canonical entity definitions
CANONICAL_ENTITIES: List[Entity] = [
    Entity(
        entity_id="HPU",
        canonical_name="Hydraulic Power Unit",
        entity_type="SUBSYSTEM",
        aliases=[
            "HPU", "Hydraulic Power Unit", "Hydraulic Unit", "HP unit", 
            "Hydraulic Power Pack", "the unit", "hydraulic pack"
        ],
        location="Skid A, Bay 2",
        status="ACTIVE",
        description="Primary hydraulic pressure source for the press circuit. Supplies pressurized fluid under supervision of PLC-03.",
        notes="Standard documentation uses 'Hydraulic Power Unit', while maintenance and training informal materials use 'HP unit' or 'Hydraulic Power Pack'."
    ),
    Entity(
        entity_id="IV-21",
        canonical_name="Isolation Valve 21",
        entity_type="VALVE",
        aliases=[
            "IV-21", "IV21", "Isolation Valve 21", "Isolation Valve", 
            "IV-21 SOLENOID", "IV-21 VALVE", "valve_iv21"
        ],
        location="Hydraulic Module",
        status="ACTIVE",
        description="Isolates the HPU from the press circuit. Must be OPEN prior to HPU startup.",
        notes="Supervised by PLC-03. Solenoid driven via 24VDC driver output."
    ),
    Entity(
        entity_id="PS-04",
        canonical_name="Pressure Sensor 04",
        entity_type="SENSOR",
        aliases=[
            "PS-04", "PS04", "P04", "PRESSURE SENSOR 04", "Pressure Sensor 04", 
            "sensor_ps04", "sensor_ps04_legacy"
        ],
        location="HPU discharge line",
        status="SUPERSEDED",
        description="Original HPU discharge pressure transducer used on software revisions prior to 3.2. Operating setpoint 180 bar.",
        notes="Superseded by PS-04A per ECN-1042 due to signal drift after ~18 months continuous operation triggering nuisance A19 alarms. Must NOT be merged with PS-04A or PS-40."
    ),
    Entity(
        entity_id="PS-04A",
        canonical_name="Pressure Sensor 04A",
        entity_type="SENSOR",
        aliases=[
            "PS-04A", "PS04A", "P04A", "Pressure Sensor 04A", "P.S. 04-A", 
            "P.S.04-A", "sensor_ps04a", "PRESSURE XDCR"
        ],
        location="HPU discharge line",
        status="ACTIVE",
        description="Updated HPU discharge pressure transducer active on software revision 3.2 and later. Operating setpoint 200 bar, 4-20mA loop.",
        notes="Introduced by ECN-1042. Requires firmware >= 3.2. Physical label on device reads 'P.S. 04-A' as confirmed on Diagnostics screen."
    ),
    Entity(
        entity_id="PS-40",
        canonical_name="Pressure Sensor 40",
        entity_type="SENSOR",
        aliases=[
            "PS-40", "PS40", "P40", "Pressure Sensor 40", "sensor_ps40"
        ],
        location="Coolant Loop, Skid B",
        status="ACTIVE",
        description="Pressure sensor dedicated to the auxiliary coolant loop on Skid B. Completely unrelated to the HPU discharge circuit.",
        notes="CRITICAL DISAMBIGUATION: PS-40 shares a numerical prefix with PS-04 but is situated in a different loop on a different skid. Never merge with PS-04 or PS-04A."
    ),
    Entity(
        entity_id="PLC-03",
        canonical_name="HCS Controller",
        entity_type="CONTROLLER",
        aliases=[
            "PLC-03", "PLC03", "HCS Controller", "Controller", "Aegis Controller", 
            "PLC-03 I/O RACK", "PLC-03 24VDC", "controller_id"
        ],
        location="Control Cabinet 1",
        status="ACTIVE",
        description="Supervises startup sequencing, pressure regulation, alarm monitoring, and safety interlocks.",
        notes="Resetting blocked in firmware above 50 bar to prevent uncommanded valve transition."
    ),
    Entity(
        entity_id="A17",
        canonical_name="Alarm A17: Hydraulic Pressure Low",
        entity_type="ALARM",
        aliases=["A17", "Alarm A17", "hydraulic_pressure_low"],
        location="N/A (Software Alarm)",
        status="ACTIVE",
        description="Triggers when HPU discharge pressure drops below 150 bar. Panel indication: RED. If persistent > 10s, requires Shutdown Procedure 4.7.",
        notes="Evaluated against active sensor (PS-04 pre-3.2, PS-04A post-3.2 per ECN-1058)."
    ),
    Entity(
        entity_id="A18",
        canonical_name="Alarm A18: Hydraulic Pressure High",
        entity_type="ALARM",
        aliases=["A18", "Alarm A18", "hydraulic_pressure_high"],
        location="N/A (Software Alarm)",
        status="ACTIVE",
        description="Triggers when HPU discharge pressure exceeds 220 bar. Panel indication: AMBER. Requires stopping HPU immediately.",
        notes="Possible causes: relief valve fault or setpoint misconfiguration."
    ),
    Entity(
        entity_id="A19",
        canonical_name="Alarm A19: Pressure Sensor Signal Invalid",
        entity_type="ALARM",
        aliases=["A19", "Alarm A19", "pressure_sensor_signal_invalid"],
        location="N/A (Software Alarm)",
        status="ACTIVE",
        description="Triggers when pressure sensor signal is out of bounds or drifting. Panel indication: RED. Requires sensor replacement.",
        notes="Historical cause on PS-04 was sensor drift after 18 months, remedied by PS-04A."
    ),
    Entity(
        entity_id="Main Reservoir",
        canonical_name="Main Reservoir",
        entity_type="RESERVOIR",
        aliases=["Main Reservoir", "Reservoir", "fluid_level"],
        location="Hydraulic Skid A",
        status="ACTIVE",
        description="Primary hydraulic fluid storage tank equipped with sight glass level indicator.",
        notes="Fluid level must be in normal band prior to HPU startup."
    ),
    Entity(
        entity_id="Auxiliary Reservoir",
        canonical_name="Auxiliary Reservoir",
        entity_type="RESERVOIR",
        aliases=["Auxiliary Reservoir", "Aux Reservoir"],
        location="Line 4/5 Skid B",
        status="ACTIVE",
        description="Secondary reservoir that tops up main reservoir during peak press demand on Line 4/5.",
        notes="Line 4/5-specific configuration detail not covered in standard Operator Manual; introduced in training deck and hydraulic schematic."
    ),
    Entity(
        entity_id="Press Circuit",
        canonical_name="Press Circuit",
        entity_type="SUBSYSTEM",
        aliases=["Press Circuit", "downstream press circuit"],
        location="Downstream of IV-21",
        status="ACTIVE",
        description="The hydraulic actuator and valve circuit driving the press operation.",
        notes="Supplied by HPU via isolation valve IV-21."
    ),
    Entity(
        entity_id="Q1",
        canonical_name="Main Disconnect Q1",
        entity_type="ELECTRICAL_DEVICE",
        aliases=["Q1", "MAIN DISCONNECT Q1", "Main Disconnect"],
        location="Control Cabinet 1",
        status="ACTIVE",
        description="Incoming 480V electrical main power disconnect switch.",
        notes="Standard incoming voltage is 480V 3-phase."
    ),
    Entity(
        entity_id="T1",
        canonical_name="Control Transformer T1",
        entity_type="ELECTRICAL_DEVICE",
        aliases=["T1", "CONTROL XFMR T1", "Control Transformer"],
        location="Control Cabinet 1",
        status="ACTIVE",
        description="Steps incoming 480V power down to 120V for control circuits.",
        notes="480:120V ratio."
    ),
    Entity(
        entity_id="TB-7",
        canonical_name="Terminal Block 7",
        entity_type="ELECTRICAL_DEVICE",
        aliases=["TB-7", "Terminal Block TB-7", "TB7"],
        location="Control Cabinet 1",
        status="ACTIVE",
        description="Wiring terminal block interfacing the 4-20mA pressure transducer loop to PLC-03.",
        notes="Corresponds to PS-04A signal loop wiring designation in AEG-DWG-W03."
    )
]


class EntityResolver:
    """Provides disambiguation, alias resolution, and non-obvious decision audits."""

    def __init__(self):
        self.entities_by_id: Dict[str, Entity] = {e.entity_id: e for e in CANONICAL_ENTITIES}
        self.alias_map: Dict[str, str] = {}
        self.decision_log: List[Dict[str, Any]] = []

        # Populate alias index
        for e in CANONICAL_ENTITIES:
            # Map canonical id
            self.alias_map[e.entity_id.upper()] = e.entity_id
            self.alias_map[e.canonical_name.upper()] = e.entity_id
            for alias in e.aliases:
                self.alias_map[alias.upper()] = e.entity_id
                # Strip hyphens and spaces for lenient matching
                cleaned = re.sub(r"[\s\-_.]", "", alias.upper())
                if cleaned:
                    self.alias_map[cleaned] = e.entity_id

    def resolve(self, text: str) -> Optional[Entity]:
        """Resolve a free-text name or query to a canonical Entity object."""
        if not text:
            return None
        text_clean = text.strip()
        
        # Exact alias match
        upper = text_clean.upper()
        if upper in self.alias_map:
            return self.entities_by_id[self.alias_map[upper]]

        # Cleaned match (no punctuation)
        stripped = re.sub(r"[\s\-_.]", "", upper)
        if stripped in self.alias_map:
            return self.entities_by_id[self.alias_map[stripped]]

        # Substring / pattern matching
        for e in CANONICAL_ENTITIES:
            if e.entity_id.upper() == upper or e.canonical_name.upper() == upper:
                return e
            for a in e.aliases:
                if a.upper() == upper:
                    return e

        return None

    def compare_components(self, comp1: str, comp2: str) -> Tuple[bool, str]:
        """
        Determine if two component references designate the same physical or logical component.
        Strictly enforces domain boundaries and documents non-obvious reasoning.
        """
        c1 = comp1.strip().upper()
        c2 = comp2.strip().upper()

        # Specific Pair: PS-04 vs PS-04A
        if (c1 in ["PS-04", "PS04", "P04"] and c2 in ["PS-04A", "PS04A", "P04A", "P.S. 04-A", "P.S.04-A"]) or \
           (c2 in ["PS-04", "PS04", "P04"] and c1 in ["PS-04A", "PS04A", "P04A", "P.S. 04-A", "P.S.04-A"]):
            rationale = (
                "NON-OBVIOUS DECISION: PS-04 and PS-04A are NOT the same component. "
                "Per Engineering Change Notice ECN-1042, PS-04 is the original sensor (target: 180 bar) "
                "which was superseded by PS-04A (target: 200 bar, updated conditioning circuit) effective "
                "software revision 3.2. PS-04A is not a form-fit-function replacement and requires firmware >= 3.2. "
                "They are separate physical parts with distinct electrical characteristics."
            )
            self._log_decision("COMPARE_COMPONENTS", comp1, comp2, False, rationale)
            return False, rationale

        # Specific Pair: PS-04 vs PS-40
        if (c1 in ["PS-04", "PS04", "P04"] and c2 in ["PS-40", "PS40", "P40"]) or \
           (c2 in ["PS-04", "PS04", "P04"] and c1 in ["PS-40", "PS40", "P40"]):
            rationale = (
                "NON-OBVIOUS DECISION: PS-04 and PS-40 are completely separate components. "
                "PS-04 was the discharge pressure sensor for the Hydraulic Power Unit on Skid A. "
                "PS-40 is a pressure sensor installed in the Coolant Loop on Skid B. "
                "Despite similar alphanumeric tags, they operate in completely different subsystems and circuits."
            )
            self._log_decision("COMPARE_COMPONENTS", comp1, comp2, False, rationale)
            return False, rationale

        # Specific Pair: PS-04A vs PS-40
        if (c1 in ["PS-04A", "PS04A", "P04A"] and c2 in ["PS-40", "PS40", "P40"]) or \
           (c2 in ["PS-04A", "PS04A", "P04A"] and c1 in ["PS-40", "PS40", "P40"]):
            rationale = (
                "NON-OBVIOUS DECISION: PS-04A and PS-40 are completely separate components. "
                "PS-04A monitors HPU discharge pressure (Skid A), whereas PS-40 monitors the Coolant Loop (Skid B)."
            )
            self._log_decision("COMPARE_COMPONENTS", comp1, comp2, False, rationale)
            return False, rationale

        # Specific Pair: PS-04A vs P.S. 04-A (Screenshot label)
        if (c1 in ["PS-04A", "PS04A"] and c2 in ["P.S. 04-A", "P.S.04-A", "P.S. 04 A"]) or \
           (c2 in ["PS-04A", "PS04A"] and c1 in ["P.S. 04-A", "P.S.04-A", "P.S. 04 A"]):
            rationale = (
                "NON-OBVIOUS DECISION: P.S. 04-A matches PS-04A. The Diagnostics screen (screen_03_diagnostics.png) "
                "explicitly includes the note: 'this screen displays the sensor tag as printed on the physical unit label'. "
                "This confirms 'P.S. 04-A' is the verbatim physical label formatting for canonical entity PS-04A."
            )
            self._log_decision("COMPARE_COMPONENTS", comp1, comp2, True, rationale)
            return True, rationale

        # General canonical resolution
        e1 = self.resolve(comp1)
        e2 = self.resolve(comp2)
        if e1 and e2:
            same = (e1.entity_id == e2.entity_id)
            rationale = (
                f"Resolved '{comp1}' -> Canonical [{e1.entity_id}] and '{comp2}' -> Canonical [{e2.entity_id}]. "
                f"Same component: {same}."
            )
            self._log_decision("COMPARE_COMPONENTS", comp1, comp2, same, rationale)
            return same, rationale

        rationale = f"Could not establish equivalence between '{comp1}' and '{comp2}' due to insufficient entity definitions."
        self._log_decision("COMPARE_COMPONENTS", comp1, comp2, False, rationale)
        return False, rationale

    def _log_decision(self, op: str, item1: str, item2: str, result: bool, rationale: str):
        self.decision_log.append({
            "operation": op,
            "item1": item1,
            "item2": item2,
            "result": result,
            "rationale": rationale
        })

    def get_all_canonical_entities(self) -> List[Entity]:
        return CANONICAL_ENTITIES

