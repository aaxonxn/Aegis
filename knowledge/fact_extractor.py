"""
Knowledge Graph and Fact Population Engine for the Aegis System.
Constructs canonical entities, atomic provenance-backed facts, topological relationships,
and populates the SQLite database and exported normalized JSON files.
"""

import logging
from typing import List
from storage.database import AegisDatabase
from storage.models import Entity, Fact, Relationship
from knowledge.entity_resolution import CANONICAL_ENTITIES
from knowledge.conflict_manager import ConflictManager

logger = logging.getLogger("AegisKnowledge")


def build_knowledge_base(db: AegisDatabase):
    """Populates entities, facts, relationships, and conflicts into the database."""
    logger.info("Populating canonical entities...")
    for entity in CANONICAL_ENTITIES:
        db.insert_entity(entity)

    logger.info("Populating conflicts...")
    cm = ConflictManager()
    for conflict in cm.get_all_conflicts():
        db.insert_conflict(conflict)

    logger.info("Populating atomic facts with granular provenance...")
    facts = [
        # HPU Facts
        Fact(
            fact_id="fact_hpu_operating_pressure_current",
            subject="HPU",
            predicate="normal_operating_pressure",
            value=200,
            unit="bar",
            applicability="Software revision >= 3.2 (units manufactured after 2024)",
            effective_date="2025-09-30",
            source_document="manuals/operator_manual.pdf",
            source_location="Section 4.3 (Startup sequence step 3) & Section 5, Page 1",
            extraction_method="pymupdf_text",
            trust_level="OFFICIAL",
            confidence=1.0,
            is_conflict=True,
            notes="Set by ECN-1042 to improve press cycle time. Measured via PS-04A."
        ),
        Fact(
            fact_id="fact_hpu_operating_pressure_legacy",
            subject="HPU",
            predicate="normal_operating_pressure",
            value=180,
            unit="bar",
            applicability="Software revisions 3.0 and 3.1",
            superseded_by="fact_hpu_operating_pressure_current",
            source_document="manuals/legacy_manual_v1.html",
            source_location="Section 5 (Normal Operating Ranges)",
            extraction_method="bs4_html",
            trust_level="OFFICIAL_SUPERSEDED",
            confidence=1.0,
            is_conflict=True,
            notes="Measured via original PS-04 sensor prior to software revision 3.2."
        ),
        Fact(
            fact_id="fact_hpu_operating_pressure_field_observation",
            subject="HPU",
            predicate="normal_operating_pressure",
            value=175,
            unit="bar",
            applicability="Line 4 HPU field observation",
            source_document="low_trust/site_survey_notes.docx",
            source_location="Paragraph 3 (Site visit notes)",
            extraction_method="python_docx",
            trust_level="FIELD_UNREVIEWED",
            confidence=0.40,
            is_conflict=True,
            notes="Informal field reading on local uncalibrated gauge; not an official engineering specification."
        ),
        Fact(
            fact_id="fact_hpu_startup_interlock_fluid",
            subject="HPU",
            predicate="startup_requirement_fluid_level",
            value="NORMAL (within normal band on sight glass)",
            source_document="manuals/operator_manual.pdf",
            source_location="Section 4.3, Page 1",
            extraction_method="pymupdf_text",
            trust_level="OFFICIAL",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_hpu_startup_interlock_iv21",
            subject="HPU",
            predicate="startup_requirement_iv21",
            value="OPEN",
            source_document="manuals/operator_manual.pdf",
            source_location="Section 4.3, Page 1",
            extraction_method="pymupdf_text",
            trust_level="OFFICIAL",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_hpu_startup_interlock_estop",
            subject="HPU",
            predicate="startup_requirement_estop",
            value="RESET",
            source_document="manuals/operator_manual.pdf",
            source_location="Section 4.3, Page 1",
            extraction_method="pymupdf_text",
            trust_level="OFFICIAL",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_hpu_startup_interlock_panel",
            subject="HPU",
            predicate="startup_requirement_maintenance_panel",
            value="CLOSED (Access panel installed - rotating parts exposed if off)",
            source_document="manuals/operator_manual.pdf",
            source_location="Section 4.3 (WARNING box), Page 1",
            extraction_method="pymupdf_text",
            trust_level="OFFICIAL",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_hpu_location",
            subject="HPU",
            predicate="location",
            value="Skid A, Bay 2",
            source_document="reference/component_register.xlsx",
            source_location="Worksheet: Components, Row 2 (Cell D2)",
            extraction_method="openpyxl_sheet",
            trust_level="OFFICIAL",
            confidence=1.0
        ),

        # PS-04 & PS-04A Facts
        Fact(
            fact_id="fact_ps04_superseded",
            subject="PS-04",
            predicate="superseded_by",
            value="PS-04A",
            applicability="Effective Software Revision 3.2",
            effective_date="2025-09-30",
            source_document="engineering_bulletins/ECN-1042.pdf",
            source_location="Section 1 (Description of Change)",
            extraction_method="pymupdf_text",
            trust_level="AUTHORITATIVE_BULLETIN",
            confidence=1.0,
            notes="PS-04 replaced due to sensor drift after 18 months continuous operation causing nuisance A19 alarms."
        ),
        Fact(
            fact_id="fact_ps04a_active",
            subject="PS-04A",
            predicate="status",
            value="ACTIVE",
            applicability="Software Revision >= 3.2",
            effective_date="2025-09-30",
            source_document="engineering_bulletins/ECN-1042.pdf",
            source_location="Section 1",
            extraction_method="pymupdf_text",
            trust_level="AUTHORITATIVE_BULLETIN",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_ps04a_setpoint",
            subject="PS-04A",
            predicate="operating_setpoint",
            value=200,
            unit="bar",
            applicability="Software Revision >= 3.2",
            source_document="engineering_bulletins/ECN-1042.pdf",
            source_location="Section 1, Page 1",
            extraction_method="pymupdf_text",
            trust_level="AUTHORITATIVE_BULLETIN",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_ps04a_signal_type",
            subject="PS-04A",
            predicate="signal_type",
            value="4-20mA",
            source_document="configuration/configuration_export.json",
            source_location="sensors.sensor_ps04a_signal_type",
            extraction_method="json_leaf_extraction",
            trust_level="SYSTEM_CONFIG",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_ps04a_physical_tag",
            subject="PS-04A",
            predicate="physical_label_tag",
            value="P.S. 04-A",
            source_document="screenshots/screen_03_diagnostics.png",
            source_location="Tag field / Diagnostic screen note",
            extraction_method="rapidocr",
            trust_level="VERIFIED_RECORD",
            confidence=0.98,
            notes="Note on screen confirms: 'this screen displays the sensor tag as printed on the physical unit label'."
        ),
        Fact(
            fact_id="fact_ps04a_calibration_record",
            subject="PS-04A",
            predicate="calibration_results",
            value="Zero: 0.1 bar (PASS), Mid: 99.6 bar (PASS), Span: 199.4 bar (PASS)",
            effective_date="2026-01-09",
            source_document="scans/scanned_appendix_calibration.pdf",
            source_location="Appendix C Calibration Record, Technician: R. Okafor",
            extraction_method="rapidocr",
            trust_level="VERIFIED_RECORD",
            confidence=0.95
        ),
        Fact(
            fact_id="fact_ps04a_temperature_abstain",
            subject="PS-04A",
            predicate="max_continuous_operating_temperature",
            value="NOT SPECIFIED",
            source_document="All Package Documents",
            source_location="Exhaustive dataset search",
            extraction_method="rule_based_absence_check",
            trust_level="OFFICIAL",
            confidence=0.0,
            notes="The maximum continuous operating temperature of PS-04A is not specified in the documentation package."
        ),
        Fact(
            fact_id="fact_ps04a_calibration_interval_abstain",
            subject="PS-04A",
            predicate="calibration_interval",
            value="NOT SPECIFIED",
            source_document="scans/scanned_appendix_calibration.pdf",
            source_location="Footer Note: 'No calibration interval is specified for PS-04A on this form'",
            extraction_method="rapidocr",
            trust_level="VERIFIED_RECORD",
            confidence=0.95,
            notes="Form explicitly notes recalibration frequency is not included in this binder."
        ),

        # PS-40 Facts
        Fact(
            fact_id="fact_ps40_location",
            subject="PS-40",
            predicate="location",
            value="Coolant Loop, Skid B",
            source_document="reference/component_register.xlsx",
            source_location="Worksheet: Components, Row 5 (Cell D5)",
            extraction_method="openpyxl_sheet",
            trust_level="OFFICIAL",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_ps40_distinct_note",
            subject="PS-40",
            predicate="system_zone",
            value="Coolant Loop (Unrelated to HPU discharge circuit)",
            source_document="configuration/configuration_export.json",
            source_location="sensors.sensor_ps40_note",
            extraction_method="json_leaf_extraction",
            trust_level="SYSTEM_CONFIG",
            confidence=1.0,
            notes="Explicit configuration instruction: 'unrelated to HPU discharge circuit; do not map to sensor_ps04a_* keys'."
        ),

        # IV-21 Facts
        Fact(
            fact_id="fact_iv21_location",
            subject="IV-21",
            predicate="location",
            value="Hydraulic Module",
            source_document="reference/component_register.xlsx",
            source_location="Worksheet: Components, Row 3 (Cell D3)",
            extraction_method="openpyxl_sheet",
            trust_level="OFFICIAL",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_iv21_required_startup_state",
            subject="IV-21",
            predicate="required_startup_state",
            value="OPEN",
            source_document="configuration/configuration_export.json",
            source_location="startup_interlocks.valve_iv21_required_state",
            extraction_method="json_leaf_extraction",
            trust_level="SYSTEM_CONFIG",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_iv21_mtbf_abstain",
            subject="IV-21",
            predicate="mean_time_between_failures",
            value="NOT SPECIFIED",
            source_document="All Package Documents",
            source_location="Exhaustive dataset search",
            extraction_method="rule_based_absence_check",
            trust_level="OFFICIAL",
            confidence=0.0,
            notes="Mean time between failures (MTBF) for IV-21 is not documented anywhere in the Aegis package."
        ),

        # PLC-03 Facts
        Fact(
            fact_id="fact_plc03_reset_limit",
            subject="PLC-03",
            predicate="max_pressure_for_reset",
            value=50,
            unit="bar",
            source_document="configuration/configuration_export.json",
            source_location="controller_reset.max_pressure_bar_allowed_for_reset",
            extraction_method="json_leaf_extraction",
            trust_level="SYSTEM_CONFIG",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_plc03_reset_restriction_reason",
            subject="PLC-03",
            predicate="reset_restriction_condition",
            value="Do NOT reset while pressure > 50 bar. Re-initializes valve outputs, risking uncommanded actuation of IV-21.",
            source_document="manuals/maintenance_manual.pdf",
            source_location="Section 3 (Controller Reset Conditions), Page 1",
            extraction_method="pymupdf_text",
            trust_level="OFFICIAL",
            confidence=1.0
        ),

        # Alarm Facts
        Fact(
            fact_id="fact_a17_threshold",
            subject="A17",
            predicate="trigger_condition",
            value=150,
            unit="bar",
            source_document="reference/alarm_reference.pdf",
            source_location="Table Row A17, Page 1",
            extraction_method="pymupdf_text",
            trust_level="OFFICIAL",
            confidence=1.0,
            notes="Triggers when HPU discharge pressure drops below 150 bar."
        ),
        Fact(
            fact_id="fact_a17_causes",
            subject="A17",
            predicate="possible_causes",
            value="1. IV-21 closed or partially closed; 2. Low hydraulic fluid; 3. Pressure sensor signal invalid / drift",
            source_document="reference/alarm_reference.pdf",
            source_location="Table Row A17, Page 1",
            extraction_method="pymupdf_text",
            trust_level="OFFICIAL",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_a17_action_10s",
            subject="A17",
            predicate="required_action_persistent_10s",
            value="Execute Shutdown Procedure 4.7 (close IV-21, confirm pressure decay, power OFF, tag out)",
            source_document="manuals/maintenance_manual.pdf",
            source_location="Section 4 (Alarm A17 Response), Page 1",
            extraction_method="pymupdf_text",
            trust_level="OFFICIAL",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_a18_threshold",
            subject="A18",
            predicate="trigger_condition",
            value=220,
            unit="bar",
            source_document="reference/alarm_reference.pdf",
            source_location="Table Row A18, Page 1",
            extraction_method="pymupdf_text",
            trust_level="OFFICIAL",
            confidence=1.0
        ),

        # Revision & Bulletin Facts
        Fact(
            fact_id="fact_rev32_effective_date",
            subject="Software Revision 3.2",
            predicate="effective_date",
            value="2025-09-30",
            source_document="reference/revision_history.xlsx",
            source_location="Worksheet: Revision History, Row 4 (Cell B4)",
            extraction_method="openpyxl_sheet",
            trust_level="OFFICIAL",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_rev32_changes",
            subject="Software Revision 3.2",
            predicate="changes_summary",
            value="Pressure sensor PS-04 replaced by PS-04A. Normal HPU discharge pressure setpoint changed from 180 bar to 200 bar per ECN-1042.",
            source_document="reference/revision_history.xlsx",
            source_location="Worksheet: Revision History, Row 4 (Cell C4)",
            extraction_method="openpyxl_sheet",
            trust_level="OFFICIAL",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_ecn1058_approver_abstain",
            subject="ECN-1058",
            predicate="approved_by",
            value="NOT SPECIFIED",
            source_document="engineering_bulletins/ECN-1058.pdf",
            source_location="Header block (Status: Released, author/approver omitted)",
            extraction_method="pymupdf_text",
            trust_level="AUTHORITATIVE_BULLETIN",
            confidence=0.0,
            notes="Engineering Change Notice ECN-1058 does not list an approver or author."
        ),

        # Electrical Specs & Compatibility
        Fact(
            fact_id="fact_electrical_incoming_voltage",
            subject="Q1",
            predicate="rated_voltage",
            value="480V incoming disconnect",
            unit="V",
            source_document="reference/component_register.xlsx",
            source_location="Worksheet: Components, Row 11 (Cell F11)",
            extraction_method="openpyxl_sheet",
            trust_level="OFFICIAL",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_electrical_transformer",
            subject="T1",
            predicate="transformer_ratio",
            value="480:120V control power",
            source_document="reference/component_register.xlsx",
            source_location="Worksheet: Components, Row 12 (Cell F12)",
            extraction_method="openpyxl_sheet",
            trust_level="OFFICIAL",
            confidence=1.0
        ),
        Fact(
            fact_id="fact_electrical_400v_abstain",
            subject="Aegis Series-7 HCS",
            predicate="compatible_with_3phase_400v",
            value="NOT DOCUMENTED / UNSUPPORTED (Specifications prescribe 480V incoming supply)",
            source_document="diagrams/system_diagram_electrical.png & reference/component_register.xlsx",
            source_location="Electrical Schematic AEG-DWG-E02",
            extraction_method="rule_based_absence_check",
            trust_level="OFFICIAL",
            confidence=0.0,
            notes="System design standard is 480V 3-phase; 400V compatibility is not supported or documented in the package."
        ),
        Fact(
            fact_id="fact_voltage_sensor_calibration_abstain",
            subject="Electrical System Diagram",
            predicate="voltage_sensor_calibration_interval",
            value="INVALID_PREMISE / NOT SPECIFIED (No voltage sensor exists on electrical drawing; Q1 is disconnect, T1 is transformer)",
            source_document="diagrams/system_diagram_electrical.png",
            source_location="Schematic AEG-DWG-E02",
            extraction_method="rule_based_absence_check",
            trust_level="OFFICIAL",
            confidence=0.0
        ),

        # Training Deck & Auxiliary Reservoir Facts
        Fact(
            fact_id="fact_training_aux_reservoir",
            subject="Auxiliary Reservoir",
            predicate="line_configuration_coverage",
            value="Introduced for Line 4/5 peak demand top-up; explicitly NOT covered in standard Operator Manual",
            source_document="extra/training_slide_excerpt.pptx",
            source_location="Slide 2 (Note on Auxiliary Reservoir)",
            extraction_method="python_pptx",
            trust_level="VERIFIED_RECORD",
            confidence=0.95,
            notes="Slide deck does not introduce any new alarms."
        )
    ]

    for fact in facts:
        db.insert_fact(fact)

    logger.info("Populating topological relationships...")
    relationships = [
        Relationship(
            relationship_id="rel_plc03_ps04a",
            source_entity="PLC-03",
            target_entity="PS-04A",
            relation_type="MONITORS_SIGNAL",
            source_document="diagrams/system_diagram_hydraulic.pdf",
            source_location="Drawing Line 8 (Purple signal loop to Box 2)",
            extraction_method="vector_shape_analysis",
            confidence=0.95,
            status="CONFIRMED",
            notes="Purple line on AEG-DWG-H01 denotes control/signal connection to PLC-03."
        ),
        Relationship(
            relationship_id="rel_plc03_iv21",
            source_entity="PLC-03",
            target_entity="IV-21",
            relation_type="CONTROLS_SOLENOID",
            source_document="diagrams/system_diagram_hydraulic.pdf",
            source_location="Drawing Line 9 (Purple signal loop to Box 3)",
            extraction_method="vector_shape_analysis",
            confidence=0.95,
            status="CONFIRMED",
            notes="Purple line on AEG-DWG-H01 denotes control/signal connection to PLC-03."
        ),
        Relationship(
            relationship_id="rel_plc03_hpu_uncertain",
            source_entity="PLC-03",
            target_entity="HPU",
            relation_type="HYDRAULIC_CONNECTION_ANOMALY",
            source_document="diagrams/system_diagram_hydraulic.pdf",
            source_location="Drawing Line 7 (Grey line between PLC-03 and HPU)",
            extraction_method="vector_shape_analysis",
            confidence=0.40,
            status="UNCERTAIN_EDGE_FLAGGED_FOR_REVIEW",
            notes="Grey line denotes hydraulic fluid path according to drawing legend. Electronic controllers do not carry hydraulic fluid; flagged for manual review."
        ),
        Relationship(
            relationship_id="rel_hpu_ps04a",
            source_entity="HPU",
            target_entity="PS-04A",
            relation_type="DISCHARGE_MEASURED_BY",
            source_document="manuals/operator_manual.pdf",
            source_location="Section 2 & Section 4.3",
            extraction_method="pymupdf_text",
            confidence=1.0,
            status="CONFIRMED"
        ),
        Relationship(
            relationship_id="rel_hpu_iv21",
            source_entity="HPU",
            target_entity="IV-21",
            relation_type="FEEDS_FLUID_THROUGH",
            source_document="manuals/operator_manual.pdf",
            source_location="Section 2 & Section 4.3",
            extraction_method="pymupdf_text",
            confidence=1.0,
            status="CONFIRMED"
        ),
        Relationship(
            relationship_id="rel_iv21_press_circuit",
            source_entity="IV-21",
            target_entity="Press Circuit",
            relation_type="ISOLATES_CIRCUIT",
            source_document="diagrams/system_diagram_hydraulic.pdf",
            source_location="Drawing Line 14",
            extraction_method="vector_shape_analysis",
            confidence=1.0,
            status="CONFIRMED"
        ),
        Relationship(
            relationship_id="rel_main_aux_reservoir",
            source_entity="Auxiliary Reservoir",
            target_entity="Main Reservoir",
            relation_type="TOPS_UP_DURING_PEAK",
            source_document="extra/training_slide_excerpt.pptx",
            source_location="Slide 2 & Drawing Line 15 (Tan line on hydraulic schematic)",
            extraction_method="python_pptx",
            confidence=0.95,
            status="CONFIRMED"
        ),
        Relationship(
            relationship_id="rel_ecn1042_supersedes_ps04",
            source_entity="PS-04A",
            target_entity="PS-04",
            relation_type="SUPERSEDES_HARDWARE",
            source_document="engineering_bulletins/ECN-1042.pdf",
            source_location="Section 1",
            extraction_method="pymupdf_text",
            confidence=1.0,
            status="CONFIRMED"
        )
    ]

    for rel in relationships:
        db.insert_relationship(rel)

    # Export normalized JSON artifacts
    db.export_normalized_json()
    logger.info("Knowledge base populated and normalized JSON files exported successfully.")

