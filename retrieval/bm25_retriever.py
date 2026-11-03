"""
BM25 Lexical Retriever for Aegis Document Chunks.
Provides fast, keyword-aware search with exact citation provenance and scoring.
"""

import re
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi
from storage.database import AegisDatabase
from storage.models import DocumentChunk, Evidence


def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text for lexical matching."""
    tokens = re.findall(r"[A-Za-z0-9_\-\.]+", text.lower())
    return tokens


class BM25Retriever:
    def __init__(self, db: AegisDatabase):
        self.db = db
        self.chunks: List[DocumentChunk] = []
        self.doc_map: Dict[str, Any] = {}
        self.bm25: BM25Okapi = None
        self._build_index()

    def _build_index(self):
        """Load all chunks and documents to build BM25 index."""
        self.chunks = self.db.get_all_chunks()
        docs = self.db.get_all_documents()
        self.doc_map = {d.filename: d for d in docs}

        tokenized_corpus = [tokenize(c.content) for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float, Dict[str, Any]]]:
        """
        Retrieve top_k chunks for query.
        Returns list of tuples: (DocumentChunk, score, document_metadata)
        """
        if not query.strip() or not self.chunks:
            return []

        query_tokens = tokenize(query)
        scores = self.bm25.get_scores(query_tokens)

        # Pair chunks with scores
        scored_chunks = list(zip(self.chunks, scores))
        # Filter non-zero and sort descending
        scored_chunks = sorted(scored_chunks, key=lambda x: x[1], reverse=True)
        top_results = scored_chunks[:top_k]

        results = []
        for chunk, score in top_results:
            doc_meta = self.doc_map.get(chunk.filename)
            trust_level = doc_meta.trust_level if doc_meta else "OFFICIAL"
            trust_score = doc_meta.trust_score if doc_meta else 0.8
            results.append((chunk, float(score), {
                "trust_level": trust_level,
                "trust_score": trust_score,
                "document_id": chunk.document_id
            }))

        return results

    def get_evidence(self, query: str, top_k: int = 3) -> List[Evidence]:
        """Convenience method returning Evidence models."""
        raw = self.retrieve(query, top_k=top_k)
        evidence_list = []
        for idx, (chunk, score, meta) in enumerate(raw):
            loc_parts = []
            if chunk.page is not None:
                loc_parts.append(f"Page {chunk.page}")
            if chunk.section:
                loc_parts.append(chunk.section)
            if chunk.worksheet:
                loc_parts.append(f"Sheet: {chunk.worksheet}")
            if chunk.cell_range:
                loc_parts.append(f"Cell: {chunk.cell_range}")
            if chunk.slide is not None:
                loc_parts.append(f"Slide {chunk.slide}")
            if chunk.json_path:
                loc_parts.append(f"Path: {chunk.json_path}")

            loc_str = ", ".join(loc_parts) if loc_parts else "General"

            evidence_list.append(Evidence(
                evidence_id=f"ev_{idx+1}_{chunk.chunk_id}",
                text=chunk.content[:400],
                source_document=chunk.filename,
                source_location=loc_str,
                extraction_method=chunk.extraction_method,
                confidence=round(min(1.0, score / 15.0), 2) if score > 0 else 0.5,
                trust_level=meta["trust_level"]
            ))
        return evidence_list

