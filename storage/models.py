"""
Pydantic data models for the Aegis Knowledge Intelligence System.
Preserves full provenance, versioning, confidence, and conflict awareness.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class Document(BaseModel):
    """Represents an ingested source document."""
    document_id: str = Field(description="Unique identifier for the document")
    filename: str = Field(description="Original filename")
    filepath: str = Field(description="Relative path in dataset")
    file_format: str = Field(description="File format extension: pdf, html, xlsx, docx, pptx, json, png, scanned_pdf")
    doc_type: str = Field(description="Functional document category: manual, bulletin, reference, diagram, screenshot, scan, configuration, notes, noise")
    trust_level: str = Field(description="OFFICIAL, AUTHORITATIVE_BULLETIN, SYSTEM_CONFIG, VERIFIED_RECORD, FIELD_UNREVIEWED, NOISE")
    trust_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Numerical trust weighting")
    revision: Optional[str] = Field(default=None, description="Document revision identifier if present")
    effective_date: Optional[str] = Field(default=None, description="Effective release date")
    page_count: Optional[int] = Field(default=None, description="Page/Slide/Sheet count")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional document metadata")


class DocumentChunk(BaseModel):
    """Represents a discrete extracted chunk with granular provenance coordinates."""
    chunk_id: str = Field(description="Unique chunk identifier")
    document_id: str = Field(description="Parent document identifier")
    filename: str = Field(description="Source filename for display")
    content: str = Field(description="Extracted textual content")
    page: Optional[int] = Field(default=None, description="Page number (1-based)")
    section: Optional[str] = Field(default=None, description="Section heading or title")
    worksheet: Optional[str] = Field(default=None, description="Spreadsheet sheet name")
    cell_range: Optional[str] = Field(default=None, description="Spreadsheet cell coordinate / row index")
    slide: Optional[int] = Field(default=None, description="Presentation slide number (1-based)")
    json_path: Optional[str] = Field(default=None, description="JSON key path (e.g., sensors.sensor_ps04a_threshold_bar)")
    extraction_method: str = Field(description="Method used: pymupdf_text, rapidocr, vector_shape_analysis, bs4_html, openpyxl_sheet, python_docx, python_pptx, json_traversal")
    bounding_box: Optional[List[float]] = Field(default=None, description="Coordinates [x0, y0, x1, y1] if applicable")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Entity(BaseModel):
    """Represents a resolved domain entity with canonical ID and aliases."""
    entity_id: str = Field(description="Canonical unique ID (e.g., PS-04A, HPU, IV-21)")
    canonical_name: str = Field(description="Primary official name")
    entity_type: str = Field(description="COMPONENT, SENSOR, VALVE, CONTROLLER, ALARM, RESERVOIR, ELECTRICAL_DEVICE, SUBSYSTEM")
    aliases: List[str] = Field(default_factory=list, description="All observed alternative spellings/labels")
    location: Optional[str] = Field(default=None, description="Physical location")
    status: str = Field(default="ACTIVE", description="ACTIVE, SUPERSEDED, PLANNED, UNVERIFIED")
    description: Optional[str] = Field(default=None, description="Functional summary")
    notes: Optional[str] = Field(default=None, description="Engineering/disambiguation notes")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Fact(BaseModel):
    """Represents an atomic, provenance-backed factual assertion."""
    fact_id: str = Field(description="Unique fact identifier")
    subject: str = Field(description="Subject entity or topic (e.g. HPU, PS-04A, A17)")
    predicate: str = Field(description="Relationship or property name (e.g. normal_operating_pressure, location, superseded_by)")
    value: Any = Field(description="Scalar, string, or boolean value")
    unit: Optional[str] = Field(default=None, description="Measurement unit (e.g., bar, seconds, mA, V)")
    applicability: Optional[str] = Field(default=None, description="Condition scope, firmware revision, or hardware line")
    effective_date: Optional[str] = Field(default=None, description="Date this fact became active")
    superseded_by: Optional[str] = Field(default=None, description="ID of fact or entity that supersedes this")
    source_document: str = Field(description="Filename of the source document")
    source_location: str = Field(description="Specific location: Page, Section, Cell, Slide, or JSON path")
    extraction_method: str = Field(description="Extraction method utilized")
    trust_level: str = Field(description="Trust tier of source document")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    is_conflict: bool = Field(default=False, description="Whether this fact participates in a detected conflict")
    notes: Optional[str] = Field(default=None, description="Disambiguation or context notes")


class Relationship(BaseModel):
    """Represents a topological or semantic relationship between entities."""
    relationship_id: str = Field(description="Unique relationship ID")
    source_entity: str = Field(description="Source entity ID")
    target_entity: str = Field(description="Target entity ID")
    relation_type: str = Field(description="CONNECTS_TO, MONITORS, ISOLATES, CONTROLS, FEEDS_TO, REPLACES, WIRED_TO")
    source_document: str = Field(description="Source document filename")
    source_location: str = Field(description="Location in source document")
    extraction_method: str = Field(description="Extraction method utilized")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    status: str = Field(default="CONFIRMED", description="CONFIRMED or UNCERTAIN_EDGE_FLAGGED_FOR_REVIEW")
    notes: Optional[str] = Field(default=None, description="Topological details or anomaly remarks")


class Evidence(BaseModel):
    """Extracted text snippet or record used to back an assertion or answer."""
    evidence_id: str = Field(description="Unique evidence identifier")
    text: str = Field(description="Verbatim or extracted snippet")
    source_document: str = Field(description="Filename of the source")
    source_location: str = Field(description="Page, section, sheet/cell, slide, or json path")
    extraction_method: str = Field(description="Extraction method utilized")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    trust_level: str = Field(description="Source trust tier")


class Conflict(BaseModel):
    """Explicitly represents disagreement or revision differences between facts."""
    conflict_id: str = Field(description="Unique conflict ID")
    topic: str = Field(description="Domain topic (e.g. 'HPU Discharge Operating Pressure', 'Pressure Sensor Replacement')")
    entity_id: Optional[str] = Field(default=None, description="Associated canonical entity ID")
    conflicting_facts: List[Dict[str, Any]] = Field(description="List of competing fact representations with provenance")
    resolution_status: str = Field(description="VERSION_SCOPED, SUPERSEDED_BY_ECN, UNRELIABLE_SOURCE_DISCOUNTED, UNRESOLVED")
    resolution_rationale: str = Field(description="Detailed engineering justification of how the conflict is handled")
    preferred_fact_id: Optional[str] = Field(default=None, description="The currently active fact ID under current revision")

