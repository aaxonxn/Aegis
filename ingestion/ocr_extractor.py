"""
OCR extractor leveraging RapidOCR for scanned PDFs and raster screenshots/diagrams.
Preserves optical character recognition confidence, line coordinates, and provenance.
"""

import os
import re
import fitz
from typing import Tuple, List, Dict, Any
from rapidocr_onnxruntime import RapidOCR
from ingestion.base import BaseExtractor
from storage.models import Document, DocumentChunk


class OcrExtractor(BaseExtractor):
    def __init__(self):
        self.engine = RapidOCR()

    def extract(self, filepath: str, filename: str, doc_metadata: Dict[str, Any]) -> Tuple[Document, List[DocumentChunk]]:
        is_pdf = filename.lower().endswith(".pdf")
        format_str = "scanned_pdf" if is_pdf else "png"

        document = Document(
            document_id=f"doc_{re.sub(r'[^a-zA-Z0-9_]', '_', filename)}",
            filename=filename,
            filepath=filepath,
            file_format=format_str,
            doc_type=doc_metadata.get("doc_type", "scan" if is_pdf else "screenshot"),
            trust_level=doc_metadata.get("trust_level", "VERIFIED_RECORD"),
            trust_score=doc_metadata.get("trust_score", 0.80),
            revision=doc_metadata.get("revision"),
            effective_date=doc_metadata.get("effective_date"),
            page_count=1,
            metadata={"is_ocr": True, "ocr_engine": "rapidocr_onnxruntime"}
        )

        chunks: List[DocumentChunk] = []

        if is_pdf:
            doc = fitz.open(filepath)
            document.page_count = len(doc)
            for page_idx, page in enumerate(doc):
                page_num = page_idx + 1
                pix = page.get_pixmap(dpi=200)
                img_bytes = pix.tobytes("png")
                result, _ = self.engine(img_bytes)
                
                if result:
                    # Group text into paragraphs / sections
                    all_lines = []
                    total_conf = 0.0
                    for item_idx, item in enumerate(result):
                        bbox = item[0] # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                        text = item[1].strip()
                        conf = float(item[2])
                        all_lines.append(text)
                        total_conf += conf

                        # Individual line chunk for fine-grained coordinate retrieval
                        chunks.append(DocumentChunk(
                            chunk_id=f"{document.document_id}_p{page_num}_line_{item_idx+1}",
                            document_id=document.document_id,
                            filename=filename,
                            content=text,
                            page=page_num,
                            section=f"OCR Line {item_idx+1}",
                            extraction_method="rapidocr",
                            bounding_box=[bbox[0][0], bbox[0][1], bbox[2][0], bbox[2][1]],
                            confidence=conf,
                            metadata={"polygon": bbox}
                        ))

                    # Also create a composite page chunk for broad context
                    avg_conf = total_conf / max(len(result), 1)
                    chunks.append(DocumentChunk(
                        chunk_id=f"{document.document_id}_p{page_num}_composite",
                        document_id=document.document_id,
                        filename=filename,
                        content="\n".join(all_lines),
                        page=page_num,
                        section="Full Document OCR Text",
                        extraction_method="rapidocr_composite",
                        confidence=avg_conf,
                        metadata={"total_ocr_lines": len(result)}
                    ))
            doc.close()
        else:
            # PNG image file
            result, _ = self.engine(filepath)
            if result:
                all_lines = []
                total_conf = 0.0
                for item_idx, item in enumerate(result):
                    bbox = item[0]
                    text = item[1].strip()
                    conf = float(item[2])
                    all_lines.append(text)
                    total_conf += conf

                    chunks.append(DocumentChunk(
                        chunk_id=f"{document.document_id}_line_{item_idx+1}",
                        document_id=document.document_id,
                        filename=filename,
                        content=text,
                        page=1,
                        section=f"Image Region {item_idx+1}",
                        extraction_method="rapidocr",
                        bounding_box=[bbox[0][0], bbox[0][1], bbox[2][0], bbox[2][1]],
                        confidence=conf,
                        metadata={"polygon": bbox}
                    ))

                avg_conf = total_conf / max(len(result), 1)
                chunks.append(DocumentChunk(
                    chunk_id=f"{document.document_id}_composite",
                    document_id=document.document_id,
                    filename=filename,
                    content="\n".join(all_lines),
                    page=1,
                    section="Full Image OCR Text",
                    extraction_method="rapidocr_composite",
                    confidence=avg_conf,
                    metadata={"total_ocr_lines": len(result)}
                ))

        return document, chunks

