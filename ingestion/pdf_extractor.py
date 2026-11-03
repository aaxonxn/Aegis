"""
Born-digital PDF extractor leveraging PyMuPDF (fitz) for high-fidelity text and structural extraction.
"""

import os
import re
import fitz
from typing import Tuple, List, Dict, Any
from ingestion.base import BaseExtractor
from storage.models import Document, DocumentChunk


class BornDigitalPdfExtractor(BaseExtractor):
    def extract(self, filepath: str, filename: str, doc_metadata: Dict[str, Any]) -> Tuple[Document, List[DocumentChunk]]:
        doc = fitz.open(filepath)
        page_count = len(doc)
        
        document = Document(
            document_id=f"doc_{re.sub(r'[^a-zA-Z0-9_]', '_', filename)}",
            filename=filename,
            filepath=filepath,
            file_format="pdf",
            doc_type=doc_metadata.get("doc_type", "reference"),
            trust_level=doc_metadata.get("trust_level", "OFFICIAL"),
            trust_score=doc_metadata.get("trust_score", 0.95),
            revision=doc_metadata.get("revision"),
            effective_date=doc_metadata.get("effective_date"),
            page_count=page_count,
            metadata={
                "pdf_metadata": doc.metadata,
                "is_scanned": False
            }
        )

        chunks: List[DocumentChunk] = []

        for page_idx, page in enumerate(doc):
            page_num = page_idx + 1
            blocks = page.get_text("blocks")
            
            # Group blocks into coherent sections
            current_section = None
            page_text_blocks = []

            for b in blocks:
                text = b[4].strip()
                if not text:
                    continue
                bbox = [b[0], b[1], b[2], b[3]]
                
                # Detect section headers (e.g., "1. Overview", "4. Operating Procedures", "Section 4", etc.)
                header_match = re.match(r"^(\d+(\.\d+)*\s+[A-Z][A-Za-z0-9\s\-_–—]+)", text)
                if header_match:
                    current_section = header_match.group(1).strip()

                chunk_id = f"{document.document_id}_p{page_num}_b{len(page_text_blocks)+1}"
                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document.document_id,
                    filename=filename,
                    content=text,
                    page=page_num,
                    section=current_section,
                    extraction_method="pymupdf_text",
                    bounding_box=bbox,
                    confidence=1.0,
                    metadata={"block_no": b[5], "type": b[6]}
                ))
                page_text_blocks.append(text)

        doc.close()
        return document, chunks

