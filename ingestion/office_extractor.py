"""
Office document extractors for Excel (.xlsx), Word (.docx), and PowerPoint (.pptx).
Preserves tabular structures, cell ranges, slide numbers, and paragraph hierarchies.
"""

import os
import re
import openpyxl
from docx import Document as DocxDocument
from pptx import Presentation as PptxPresentation
from typing import Tuple, List, Dict, Any
from ingestion.base import BaseExtractor
from storage.models import Document, DocumentChunk


class ExcelExtractor(BaseExtractor):
    def extract(self, filepath: str, filename: str, doc_metadata: Dict[str, Any]) -> Tuple[Document, List[DocumentChunk]]:
        wb = openpyxl.load_workbook(filepath, data_only=True)
        sheet_count = len(wb.sheetnames)

        document = Document(
            document_id=f"doc_{re.sub(r'[^a-zA-Z0-9_]', '_', filename)}",
            filename=filename,
            filepath=filepath,
            file_format="xlsx",
            doc_type=doc_metadata.get("doc_type", "reference"),
            trust_level=doc_metadata.get("trust_level", "OFFICIAL"),
            trust_score=doc_metadata.get("trust_score", 0.95),
            revision=doc_metadata.get("revision"),
            effective_date=doc_metadata.get("effective_date"),
            page_count=sheet_count,
            metadata={"sheets": wb.sheetnames}
        )

        chunks: List[DocumentChunk] = []

        for sname in wb.sheetnames:
            sheet = wb[sname]
            rows = list(sheet.iter_rows(values_only=True))
            if not rows:
                continue

            header = [str(c).strip() if c is not None else f"Col_{idx+1}" for idx, c in enumerate(rows[0])]

            for row_idx, r in enumerate(rows[1:], start=2):
                # Filter out completely empty rows
                if not any(r):
                    continue
                row_dict = {}
                row_str_parts = []
                for h, val in zip(header, r):
                    val_str = str(val).strip() if val is not None else ""
                    row_dict[h] = val_str
                    if val_str:
                        row_str_parts.append(f"{h}: {val_str}")

                content = " | ".join(row_str_parts)
                cell_range = f"{sname}!A{row_idx}:{chr(ord('A')+len(header)-1)}{row_idx}"
                chunk_id = f"{document.document_id}_{sname}_r{row_idx}"

                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document.document_id,
                    filename=filename,
                    content=content,
                    page=1,
                    section=f"Worksheet: {sname}",
                    worksheet=sname,
                    cell_range=cell_range,
                    extraction_method="openpyxl_sheet",
                    confidence=1.0,
                    metadata={"row_data": row_dict, "row_index": row_idx}
                ))

        return document, chunks


class DocxExtractor(BaseExtractor):
    def extract(self, filepath: str, filename: str, doc_metadata: Dict[str, Any]) -> Tuple[Document, List[DocumentChunk]]:
        doc = DocxDocument(filepath)

        document = Document(
            document_id=f"doc_{re.sub(r'[^a-zA-Z0-9_]', '_', filename)}",
            filename=filename,
            filepath=filepath,
            file_format="docx",
            doc_type=doc_metadata.get("doc_type", "reference"),
            trust_level=doc_metadata.get("trust_level", "OFFICIAL"),
            trust_score=doc_metadata.get("trust_score", 0.90),
            revision=doc_metadata.get("revision"),
            effective_date=doc_metadata.get("effective_date"),
            page_count=len(doc.paragraphs),
            metadata={"paragraph_count": len(doc.paragraphs), "table_count": len(doc.tables)}
        )

        chunks: List[DocumentChunk] = []

        # 1. Paragraphs
        current_section = "General"
        p_idx = 0
        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue
            p_idx += 1
            style_name = getattr(p.style, "name", "") if p.style else ""
            if style_name and style_name.startswith("Heading"):
                current_section = text

            chunks.append(DocumentChunk(
                chunk_id=f"{document.document_id}_p_{p_idx}",
                document_id=document.document_id,
                filename=filename,
                content=text,
                page=1,
                section=current_section,
                extraction_method="python_docx",
                confidence=1.0,
                metadata={"style": style_name}
            ))

        # 2. Tables
        for t_idx, table in enumerate(doc.tables):
            t_rows = []
            for r_idx, row in enumerate(table.rows):
                cell_texts = [c.text.strip() for c in row.cells]
                t_rows.append(cell_texts)

            if t_rows:
                header = t_rows[0]
                for r_idx, row_cells in enumerate(t_rows[1:], start=1):
                    row_parts = [f"{h}: {v}" for h, v in zip(header, row_cells) if v]
                    chunks.append(DocumentChunk(
                        chunk_id=f"{document.document_id}_t{t_idx+1}_r{r_idx}",
                        document_id=document.document_id,
                        filename=filename,
                        content=" | ".join(row_parts),
                        page=1,
                        section=f"Table {t_idx+1}",
                        cell_range=f"Table_{t_idx+1}_Row_{r_idx}",
                        extraction_method="python_docx_table",
                        confidence=1.0,
                        metadata={"header": header, "cells": row_cells}
                    ))

        return document, chunks


class PptxExtractor(BaseExtractor):
    def extract(self, filepath: str, filename: str, doc_metadata: Dict[str, Any]) -> Tuple[Document, List[DocumentChunk]]:
        prs = PptxPresentation(filepath)
        slide_count = len(prs.slides)

        document = Document(
            document_id=f"doc_{re.sub(r'[^a-zA-Z0-9_]', '_', filename)}",
            filename=filename,
            filepath=filepath,
            file_format="pptx",
            doc_type="training",
            trust_level=doc_metadata.get("trust_level", "VERIFIED_RECORD"),
            trust_score=doc_metadata.get("trust_score", 0.70),
            page_count=slide_count,
            metadata={"slide_count": slide_count}
        )

        chunks: List[DocumentChunk] = []

        for slide_idx, slide in enumerate(prs.slides):
            slide_num = slide_idx + 1
            shape_texts = []
            slide_title = f"Slide {slide_num}"

            for shape in slide.shapes:
                if shape.has_text_frame:
                    txt = shape.text.strip()
                    if txt:
                        shape_texts.append(txt)
                        # Check if title shape
                        if shape == slide.shapes.title or "title" in getattr(shape, "name", "").lower():
                            slide_title = txt.split("\n")[0]

            content = "\n".join(shape_texts)
            if content:
                chunks.append(DocumentChunk(
                    chunk_id=f"{document.document_id}_slide_{slide_num}",
                    document_id=document.document_id,
                    filename=filename,
                    content=content,
                    page=slide_num,
                    slide=slide_num,
                    section=slide_title,
                    extraction_method="python_pptx",
                    confidence=1.0,
                    metadata={"slide_shapes": len(shape_texts)}
                ))

        return document, chunks
