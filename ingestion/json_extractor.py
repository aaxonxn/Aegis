"""
JSON extractor preserving exact JSON object paths and structured machine parameters.
"""

import os
import re
import json
from typing import Tuple, List, Dict, Any
from ingestion.base import BaseExtractor
from storage.models import Document, DocumentChunk


class JsonExtractor(BaseExtractor):
    def extract(self, filepath: str, filename: str, doc_metadata: Dict[str, Any]) -> Tuple[Document, List[DocumentChunk]]:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        document = Document(
            document_id=f"doc_{re.sub(r'[^a-zA-Z0-9_]', '_', filename)}",
            filename=filename,
            filepath=filepath,
            file_format="json",
            doc_type="configuration",
            trust_level=doc_metadata.get("trust_level", "SYSTEM_CONFIG"),
            trust_score=doc_metadata.get("trust_score", 0.95),
            revision=data.get("export_metadata", {}).get("firmware_version"),
            effective_date=data.get("export_metadata", {}).get("export_timestamp"),
            page_count=1,
            metadata={"export_metadata": data.get("export_metadata", {})}
        )

        chunks: List[DocumentChunk] = []

        # Recursively traverse JSON and create leaf chunks with full json_path
        def traverse(obj: Any, path: str):
            if isinstance(obj, dict):
                # Also create a composite chunk for the section if it has multiple keys
                if path:
                    section_summary = f"Configuration Section [{path}]:\n" + json.dumps(obj, indent=2)
                    chunks.append(DocumentChunk(
                        chunk_id=f"{document.document_id}_{path.replace('.', '_')}",
                        document_id=document.document_id,
                        filename=filename,
                        content=section_summary,
                        page=1,
                        section=f"JSON Section: {path}",
                        json_path=path,
                        extraction_method="json_traversal",
                        confidence=1.0,
                        metadata={"raw_data": obj}
                    ))
                for k, v in obj.items():
                    sub_path = f"{path}.{k}" if path else k
                    traverse(v, sub_path)
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    sub_path = f"{path}[{idx}]"
                    traverse(item, sub_path)
            else:
                # Leaf primitive value
                content_str = f"Parameter '{path}' = {obj}"
                chunk_id = f"{document.document_id}_leaf_{path.replace('.', '_').replace('[', '_').replace(']', '_')}"
                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document.document_id,
                    filename=filename,
                    content=content_str,
                    page=1,
                    section=f"JSON Leaf: {path}",
                    json_path=path,
                    extraction_method="json_leaf_extraction",
                    confidence=1.0,
                    metadata={"key": path, "value": obj}
                ))

        traverse(data, "")
        return document, chunks

