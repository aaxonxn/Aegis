"""
Main Ingestion Pipeline for Aegis Knowledge Intelligence System.
Dispatches extractors across heterogeneous dataset files, records full provenance,
and stores structured documents and chunks in SQLite.
"""

import os
import time
import logging
from typing import Dict, Any, List
from storage.database import AegisDatabase
from storage.models import Document, DocumentChunk

from ingestion.pdf_extractor import BornDigitalPdfExtractor
from ingestion.ocr_extractor import OcrExtractor
from ingestion.diagram_extractor import DiagramExtractor
from ingestion.html_extractor import HtmlExtractor
from ingestion.office_extractor import ExcelExtractor, DocxExtractor, PptxExtractor
from ingestion.json_extractor import JsonExtractor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("AegisIngestion")

# Static registry of document metadata to guide trust tiers and version applicability
FILE_METADATA_REGISTRY = {
    "configuration/configuration_export.json": {
        "doc_type": "configuration",
        "trust_level": "SYSTEM_CONFIG",
        "trust_score": 0.95,
        "revision": "3.2.1",
        "effective_date": "2026-02-03"
    },
    "diagrams/system_diagram_electrical.png": {
        "doc_type": "diagram",
        "trust_level": "OFFICIAL",
        "trust_score": 0.85,
        "revision": "AEG-DWG-E02",
        "effective_date": None
    },
    "diagrams/system_diagram_hydraulic.pdf": {
        "doc_type": "diagram",
        "trust_level": "OFFICIAL",
        "trust_score": 0.85,
        "revision": "AEG-DWG-H01",
        "effective_date": None
    },
    "diagrams/wiring_diagram.pdf": {
        "doc_type": "diagram",
        "trust_level": "OFFICIAL",
        "trust_score": 0.85,
        "revision": "AEG-DWG-W03",
        "effective_date": None
    },
    "engineering_bulletins/ECN-1042.pdf": {
        "doc_type": "bulletin",
        "trust_level": "AUTHORITATIVE_BULLETIN",
        "trust_score": 1.0,
        "revision": "3.2",
        "effective_date": "2025-09-30"
    },
    "engineering_bulletins/ECN-1058.pdf": {
        "doc_type": "bulletin",
        "trust_level": "AUTHORITATIVE_BULLETIN",
        "trust_score": 1.0,
        "revision": "3.2.1",
        "effective_date": "2025-11-18"
    },
    "extra/training_slide_excerpt.pptx": {
        "doc_type": "training",
        "trust_level": "VERIFIED_RECORD",
        "trust_score": 0.70,
        "revision": None,
        "effective_date": None
    },
    "low_trust/site_survey_notes.docx": {
        "doc_type": "field_notes",
        "trust_level": "FIELD_UNREVIEWED",
        "trust_score": 0.35,
        "revision": None,
        "effective_date": None
    },
    "manuals/legacy_manual_v1.html": {
        "doc_type": "manual",
        "trust_level": "OFFICIAL_SUPERSEDED",
        "trust_score": 0.60,
        "revision": "1",
        "effective_date": "2024-03-01"
    },
    "manuals/maintenance_manual.pdf": {
        "doc_type": "manual",
        "trust_level": "OFFICIAL",
        "trust_score": 0.95,
        "revision": "3",
        "effective_date": None
    },
    "manuals/operator_manual.pdf": {
        "doc_type": "manual",
        "trust_level": "OFFICIAL",
        "trust_score": 0.95,
        "revision": "4",
        "effective_date": "2025-09-30"
    },
    "noise/safety_data_sheet_hydraulic_fluid.pdf": {
        "doc_type": "safety_data",
        "trust_level": "NOISE",
        "trust_score": 0.10,
        "revision": "HF32-SDS-06",
        "effective_date": "2025-02-11"
    },
    "reference/alarm_reference.pdf": {
        "doc_type": "reference",
        "trust_level": "OFFICIAL",
        "trust_score": 0.95,
        "revision": "5",
        "effective_date": "2025-11-18"
    },
    "reference/component_register.xlsx": {
        "doc_type": "reference",
        "trust_level": "OFFICIAL",
        "trust_score": 0.95,
        "revision": "AEG-CR-700",
        "effective_date": None
    },
    "reference/revision_history.xlsx": {
        "doc_type": "reference",
        "trust_level": "OFFICIAL",
        "trust_score": 0.95,
        "revision": None,
        "effective_date": "2025-11-18"
    },
    "reference/terminology_glossary.docx": {
        "doc_type": "reference",
        "trust_level": "OFFICIAL",
        "trust_score": 0.90,
        "revision": "2",
        "effective_date": None
    },
    "scans/scanned_appendix_calibration.pdf": {
        "doc_type": "calibration_record",
        "trust_level": "VERIFIED_RECORD",
        "trust_score": 0.80,
        "revision": None,
        "effective_date": "2026-01-09"
    },
    "screenshots/screen_01_home.png": {
        "doc_type": "screenshot",
        "trust_level": "VERIFIED_RECORD",
        "trust_score": 0.85,
        "revision": "3.2",
        "effective_date": None
    },
    "screenshots/screen_02_alarms.png": {
        "doc_type": "screenshot",
        "trust_level": "VERIFIED_RECORD",
        "trust_score": 0.85,
        "revision": "3.2",
        "effective_date": None
    },
    "screenshots/screen_03_diagnostics.png": {
        "doc_type": "screenshot",
        "trust_level": "VERIFIED_RECORD",
        "trust_score": 0.85,
        "revision": "3.2",
        "effective_date": "2026-01-09"
    }
}


class IngestionPipeline:
    def __init__(self, dataset_dir: str = "aegis-dataset", db: AegisDatabase = None):
        self.dataset_dir = dataset_dir
        self.db = db or AegisDatabase()
        
        # Instantiate extractor instances
        self.pdf_extractor = BornDigitalPdfExtractor()
        self.ocr_extractor = OcrExtractor()
        self.diagram_extractor = DiagramExtractor()
        self.html_extractor = HtmlExtractor()
        self.excel_extractor = ExcelExtractor()
        self.docx_extractor = DocxExtractor()
        self.pptx_extractor = PptxExtractor()
        self.json_extractor = JsonExtractor()

    def run(self) -> Dict[str, Any]:
        """Execute ingestion over all files in dataset_dir."""
        start_time = time.time()
        logger.info(f"Starting ingestion pipeline from {self.dataset_dir}...")

        ingested_docs: List[Document] = []
        total_chunks = 0
        failures: List[Dict[str, str]] = []
        processed_files: List[str] = []

        # Find all files in dataset
        all_filepaths = []
        for root, _, files in os.walk(self.dataset_dir):
            for f in sorted(files):
                all_filepaths.append(os.path.join(root, f))

        logger.info(f"Discovered {len(all_filepaths)} files to ingest.")

        for p in all_filepaths:
            filename = os.path.basename(p)
            rel_path = os.path.relpath(p, self.dataset_dir).replace("\\", "/")
            meta = FILE_METADATA_REGISTRY.get(rel_path, {
                "doc_type": "unknown",
                "trust_level": "OFFICIAL",
                "trust_score": 0.80
            })

            try:
                doc = None
                chunks = []
                ext = os.path.splitext(filename)[1].lower()

                # Dispatch appropriate extractor
                if filename == "system_diagram_hydraulic.pdf":
                    doc, chunks = self.diagram_extractor.extract(p, filename, meta)
                elif filename == "scanned_appendix_calibration.pdf":
                    doc, chunks = self.ocr_extractor.extract(p, filename, meta)
                elif ext == ".pdf":
                    doc, chunks = self.pdf_extractor.extract(p, filename, meta)
                elif ext == ".png":
                    doc, chunks = self.ocr_extractor.extract(p, filename, meta)
                elif ext in [".html", ".htm"]:
                    doc, chunks = self.html_extractor.extract(p, filename, meta)
                elif ext in [".xlsx", ".xls"]:
                    doc, chunks = self.excel_extractor.extract(p, filename, meta)
                elif ext == ".docx":
                    doc, chunks = self.docx_extractor.extract(p, filename, meta)
                elif ext == ".pptx":
                    doc, chunks = self.pptx_extractor.extract(p, filename, meta)
                elif ext == ".json":
                    doc, chunks = self.json_extractor.extract(p, filename, meta)
                else:
                    logger.warning(f"Unsupported file format for {filename}, skipping.")
                    continue

                if doc and chunks:
                    self.db.insert_document(doc)
                    self.db.insert_chunks(chunks)
                    ingested_docs.append(doc)
                    total_chunks += len(chunks)
                    processed_files.append(rel_path)
                    logger.info(f"Successfully ingested {rel_path}: {len(chunks)} chunks.")
                else:
                    failures.append({"file": rel_path, "error": "No document or chunks returned"})
                    logger.error(f"Failed to extract {rel_path}: No content returned.")

            except Exception as e:
                logger.exception(f"Error extracting {rel_path}: {str(e)}")
                failures.append({"file": rel_path, "error": str(e)})

        elapsed = time.time() - start_time
        summary = {
            "total_files_found": len(all_filepaths),
            "total_files_ingested": len(ingested_docs),
            "total_chunks_created": total_chunks,
            "failures_count": len(failures),
            "failures": failures,
            "processed_files": processed_files,
            "elapsed_seconds": round(elapsed, 2)
        }
        logger.info(f"Ingestion completed in {elapsed:.2f}s: {len(ingested_docs)}/{len(all_filepaths)} files, {total_chunks} chunks.")
        return summary

