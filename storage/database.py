"""
SQLite storage manager for Aegis Knowledge Intelligence System.
Handles schema creation, relational querying, provenance tracking, and JSON exports.
"""

import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
from storage.models import Document, DocumentChunk, Entity, Fact, Relationship, Evidence, Conflict


class AegisDatabase:
    def __init__(self, db_path: str = "data/processed/aegis_knowledge.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize all relational tables with appropriate indices."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Documents table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                file_format TEXT NOT NULL,
                doc_type TEXT NOT NULL,
                trust_level TEXT NOT NULL,
                trust_score REAL NOT NULL,
                revision TEXT,
                effective_date TEXT,
                page_count INTEGER,
                metadata TEXT
            );
            """)

            # Document Chunks table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                chunk_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                page INTEGER,
                section TEXT,
                worksheet TEXT,
                cell_range TEXT,
                slide INTEGER,
                json_path TEXT,
                extraction_method TEXT NOT NULL,
                bounding_box TEXT,
                confidence REAL NOT NULL,
                metadata TEXT,
                FOREIGN KEY (document_id) REFERENCES documents(document_id)
            );
            """)

            # Entities table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                canonical_name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                aliases TEXT NOT NULL,
                location TEXT,
                status TEXT NOT NULL,
                description TEXT,
                notes TEXT,
                metadata TEXT
            );
            """)

            # Facts table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                fact_id TEXT PRIMARY KEY,
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                value TEXT NOT NULL,
                unit TEXT,
                applicability TEXT,
                effective_date TEXT,
                superseded_by TEXT,
                source_document TEXT NOT NULL,
                source_location TEXT NOT NULL,
                extraction_method TEXT NOT NULL,
                trust_level TEXT NOT NULL,
                confidence REAL NOT NULL,
                is_conflict INTEGER DEFAULT 0,
                notes TEXT
            );
            """)

            # Relationships table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                relationship_id TEXT PRIMARY KEY,
                source_entity TEXT NOT NULL,
                target_entity TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                source_document TEXT NOT NULL,
                source_location TEXT NOT NULL,
                extraction_method TEXT NOT NULL,
                confidence REAL NOT NULL,
                status TEXT NOT NULL,
                notes TEXT
            );
            """)

            # Conflicts table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS conflicts (
                conflict_id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                entity_id TEXT,
                conflicting_facts TEXT NOT NULL,
                resolution_status TEXT NOT NULL,
                resolution_rationale TEXT NOT NULL,
                preferred_fact_id TEXT
            );
            """)

            # Indexes for ultra-fast lookup
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc ON document_chunks(document_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_subj ON facts(subject);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_pred ON facts(predicate);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rel_src ON relationships(source_entity);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rel_tgt ON relationships(target_entity);")

            conn.commit()

    def insert_document(self, doc: Document):
        with self.get_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO documents 
            (document_id, filename, filepath, file_format, doc_type, trust_level, trust_score, revision, effective_date, page_count, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc.document_id, doc.filename, doc.filepath, doc.file_format,
                doc.doc_type, doc.trust_level, doc.trust_score, doc.revision,
                doc.effective_date, doc.page_count, json.dumps(doc.metadata)
            ))
            conn.commit()

    def insert_chunk(self, chunk: DocumentChunk):
        with self.get_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO document_chunks
            (chunk_id, document_id, filename, content, page, section, worksheet, cell_range, slide, json_path, extraction_method, bounding_box, confidence, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chunk.chunk_id, chunk.document_id, chunk.filename, chunk.content,
                chunk.page, chunk.section, chunk.worksheet, chunk.cell_range,
                chunk.slide, chunk.json_path, chunk.extraction_method,
                json.dumps(chunk.bounding_box) if chunk.bounding_box else None,
                chunk.confidence, json.dumps(chunk.metadata)
            ))
            conn.commit()

    def insert_chunks(self, chunks: List[DocumentChunk]):
        with self.get_connection() as conn:
            conn.executemany("""
            INSERT OR REPLACE INTO document_chunks
            (chunk_id, document_id, filename, content, page, section, worksheet, cell_range, slide, json_path, extraction_method, bounding_box, confidence, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    c.chunk_id, c.document_id, c.filename, c.content,
                    c.page, c.section, c.worksheet, c.cell_range,
                    c.slide, c.json_path, c.extraction_method,
                    json.dumps(c.bounding_box) if c.bounding_box else None,
                    c.confidence, json.dumps(c.metadata)
                ) for c in chunks
            ])
            conn.commit()

    def insert_entity(self, entity: Entity):
        with self.get_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO entities
            (entity_id, canonical_name, entity_type, aliases, location, status, description, notes, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entity.entity_id, entity.canonical_name, entity.entity_type,
                json.dumps(entity.aliases), entity.location, entity.status,
                entity.description, entity.notes, json.dumps(entity.metadata)
            ))
            conn.commit()

    def insert_fact(self, fact: Fact):
        with self.get_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO facts
            (fact_id, subject, predicate, value, unit, applicability, effective_date, superseded_by, source_document, source_location, extraction_method, trust_level, confidence, is_conflict, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fact.fact_id, fact.subject, fact.predicate, json.dumps(fact.value),
                fact.unit, fact.applicability, fact.effective_date, fact.superseded_by,
                fact.source_document, fact.source_location, fact.extraction_method,
                fact.trust_level, fact.confidence, 1 if fact.is_conflict else 0, fact.notes
            ))
            conn.commit()

    def insert_relationship(self, rel: Relationship):
        with self.get_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO relationships
            (relationship_id, source_entity, target_entity, relation_type, source_document, source_location, extraction_method, confidence, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rel.relationship_id, rel.source_entity, rel.target_entity,
                rel.relation_type, rel.source_document, rel.source_location,
                rel.extraction_method, rel.confidence, rel.status, rel.notes
            ))
            conn.commit()

    def insert_conflict(self, conflict: Conflict):
        with self.get_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO conflicts
            (conflict_id, topic, entity_id, conflicting_facts, resolution_status, resolution_rationale, preferred_fact_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                conflict.conflict_id, conflict.topic, conflict.entity_id,
                json.dumps(conflict.conflicting_facts), conflict.resolution_status,
                conflict.resolution_rationale, conflict.preferred_fact_id
            ))
            conn.commit()

    # Query methods
    def get_all_documents(self) -> List[Document]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM documents ORDER BY filename").fetchall()
            return [
                Document(
                    document_id=r["document_id"],
                    filename=r["filename"],
                    filepath=r["filepath"],
                    file_format=r["file_format"],
                    doc_type=r["doc_type"],
                    trust_level=r["trust_level"],
                    trust_score=r["trust_score"],
                    revision=r["revision"],
                    effective_date=r["effective_date"],
                    page_count=r["page_count"],
                    metadata=json.loads(r["metadata"]) if r["metadata"] else {}
                ) for r in rows
            ]

    def get_all_chunks(self) -> List[DocumentChunk]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM document_chunks").fetchall()
            return [
                DocumentChunk(
                    chunk_id=r["chunk_id"],
                    document_id=r["document_id"],
                    filename=r["filename"],
                    content=r["content"],
                    page=r["page"],
                    section=r["section"],
                    worksheet=r["worksheet"],
                    cell_range=r["cell_range"],
                    slide=r["slide"],
                    json_path=r["json_path"],
                    extraction_method=r["extraction_method"],
                    bounding_box=json.loads(r["bounding_box"]) if r["bounding_box"] else None,
                    confidence=r["confidence"],
                    metadata=json.loads(r["metadata"]) if r["metadata"] else {}
                ) for r in rows
            ]

    def get_all_entities(self) -> List[Entity]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM entities ORDER BY canonical_name").fetchall()
            return [
                Entity(
                    entity_id=r["entity_id"],
                    canonical_name=r["canonical_name"],
                    entity_type=r["entity_type"],
                    aliases=json.loads(r["aliases"]) if r["aliases"] else [],
                    location=r["location"],
                    status=r["status"],
                    description=r["description"],
                    notes=r["notes"],
                    metadata=json.loads(r["metadata"]) if r["metadata"] else {}
                ) for r in rows
            ]

    def get_all_facts(self) -> List[Fact]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM facts").fetchall()
            return [
                Fact(
                    fact_id=r["fact_id"],
                    subject=r["subject"],
                    predicate=r["predicate"],
                    value=json.loads(r["value"]),
                    unit=r["unit"],
                    applicability=r["applicability"],
                    effective_date=r["effective_date"],
                    superseded_by=r["superseded_by"],
                    source_document=r["source_document"],
                    source_location=r["source_location"],
                    extraction_method=r["extraction_method"],
                    trust_level=r["trust_level"],
                    confidence=r["confidence"],
                    is_conflict=bool(r["is_conflict"]),
                    notes=r["notes"]
                ) for r in rows
            ]

    def get_all_relationships(self) -> List[Relationship]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM relationships").fetchall()
            return [
                Relationship(
                    relationship_id=r["relationship_id"],
                    source_entity=r["source_entity"],
                    target_entity=r["target_entity"],
                    relation_type=r["relation_type"],
                    source_document=r["source_document"],
                    source_location=r["source_location"],
                    extraction_method=r["extraction_method"],
                    confidence=r["confidence"],
                    status=r["status"],
                    notes=r["notes"]
                ) for r in rows
            ]

    def get_all_conflicts(self) -> List[Conflict]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM conflicts").fetchall()
            return [
                Conflict(
                    conflict_id=r["conflict_id"],
                    topic=r["topic"],
                    entity_id=r["entity_id"],
                    conflicting_facts=json.loads(r["conflicting_facts"]),
                    resolution_status=r["resolution_status"],
                    resolution_rationale=r["resolution_rationale"],
                    preferred_fact_id=r["preferred_fact_id"]
                ) for r in rows
            ]

    def export_normalized_json(self, 
                              kg_out: str = "data/processed/knowledge_graph.json",
                              facts_out: str = "data/processed/facts_export.json"):
        """Export normalized JSON datasets for interoperability."""
        os.makedirs(os.path.dirname(kg_out), exist_ok=True)
        os.makedirs(os.path.dirname(facts_out), exist_ok=True)

        kg_data = {
            "entities": [e.model_dump() for e in self.get_all_entities()],
            "relationships": [r.model_dump() for r in self.get_all_relationships()],
            "conflicts": [c.model_dump() for c in self.get_all_conflicts()]
        }
        with open(kg_out, "w", encoding="utf-8") as f:
            json.dump(kg_data, f, indent=2)

        facts_data = {
            "documents": [d.model_dump() for d in self.get_all_documents()],
            "facts": [f.model_dump() for f in self.get_all_facts()]
        }
        with open(facts_out, "w", encoding="utf-8") as f:
            json.dump(facts_data, f, indent=2)

    def get_statistics(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            doc_count = conn.execute("SELECT count(*) FROM documents").fetchone()[0]
            chunk_count = conn.execute("SELECT count(*) FROM document_chunks").fetchone()[0]
            entity_count = conn.execute("SELECT count(*) FROM entities").fetchone()[0]
            fact_count = conn.execute("SELECT count(*) FROM facts").fetchone()[0]
            rel_count = conn.execute("SELECT count(*) FROM relationships").fetchone()[0]
            conflict_count = conn.execute("SELECT count(*) FROM conflicts").fetchone()[0]

            formats = dict(conn.execute("SELECT file_format, count(*) FROM documents GROUP BY file_format").fetchall())
            trust_levels = dict(conn.execute("SELECT trust_level, count(*) FROM documents GROUP BY trust_level").fetchall())

            return {
                "document_count": doc_count,
                "chunk_count": chunk_count,
                "entity_count": entity_count,
                "fact_count": fact_count,
                "relationship_count": rel_count,
                "conflict_count": conflict_count,
                "formats": formats,
                "trust_levels": trust_levels
            }

