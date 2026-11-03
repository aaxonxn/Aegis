"""
HTML extractor for legacy manual exports using BeautifulSoup4.
Preserves hierarchy, tables, lists, and legacy supersession notices.
"""

import os
import re
from typing import Tuple, List, Dict, Any
from bs4 import BeautifulSoup
from ingestion.base import BaseExtractor
from storage.models import Document, DocumentChunk


class HtmlExtractor(BaseExtractor):
    def extract(self, filepath: str, filename: str, doc_metadata: Dict[str, Any]) -> Tuple[Document, List[DocumentChunk]]:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            raw_html = f.read()

        soup = BeautifulSoup(raw_html, "html.parser")
        title = soup.title.string.strip() if soup.title else filename

        document = Document(
            document_id=f"doc_{re.sub(r'[^a-zA-Z0-9_]', '_', filename)}",
            filename=filename,
            filepath=filepath,
            file_format="html",
            doc_type=doc_metadata.get("doc_type", "manual"),
            trust_level=doc_metadata.get("trust_level", "OFFICIAL_SUPERSEDED"),
            trust_score=doc_metadata.get("trust_score", 0.60),
            revision="1",
            effective_date="2024-03-01",
            page_count=1,
            metadata={"html_title": title, "superseded": True}
        )

        chunks: List[DocumentChunk] = []

        # 1. Supersession warning banner / disclaimer
        warning_divs = soup.find_all(class_=re.compile(r"warning|notice|banner|alert", re.I))
        for idx, w in enumerate(warning_divs):
            chunks.append(DocumentChunk(
                chunk_id=f"{document.document_id}_warning_{idx+1}",
                document_id=document.document_id,
                filename=filename,
                content=w.get_text().strip(),
                page=1,
                section="Legacy CMS Export Notice",
                extraction_method="bs4_html",
                confidence=1.0,
                metadata={"is_warning": True}
            ))

        # 2. Section-by-section extraction
        headers = soup.find_all(["h1", "h2", "h3"])
        if headers:
            for h_idx, h in enumerate(headers):
                section_title = h.get_text().strip()
                # Gather content until next header
                section_content = [section_title]
                curr = h.next_sibling
                while curr and curr.name not in ["h1", "h2", "h3"]:
                    if hasattr(curr, "get_text"):
                        txt = curr.get_text().strip()
                        if txt:
                            section_content.append(txt)
                    curr = curr.next_sibling

                full_text = "\n".join(section_content)
                chunks.append(DocumentChunk(
                    chunk_id=f"{document.document_id}_sec_{h_idx+1}",
                    document_id=document.document_id,
                    filename=filename,
                    content=full_text,
                    page=1,
                    section=section_title,
                    extraction_method="bs4_html",
                    confidence=1.0
                ))
        else:
            # Fallback to whole body
            body_text = soup.get_text().strip()
            chunks.append(DocumentChunk(
                chunk_id=f"{document.document_id}_body",
                document_id=document.document_id,
                filename=filename,
                content=body_text,
                page=1,
                section="Full Body",
                extraction_method="bs4_html",
                confidence=1.0
            ))

        return document, chunks

