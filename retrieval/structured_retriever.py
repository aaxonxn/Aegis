"""
Structured Retriever for Entities, Facts, and Relationships.
Provides direct graph traversal and property lookup for resolved domain entities.
"""

from typing import List, Dict, Any, Optional, Tuple
from storage.database import AegisDatabase
from storage.models import Entity, Fact, Relationship
from knowledge.entity_resolution import EntityResolver


class StructuredRetriever:
    def __init__(self, db: AegisDatabase, resolver: Optional[EntityResolver] = None):
        self.db = db
        self.resolver = resolver or EntityResolver()

    def get_entity_facts(self, entity_mention: str) -> Tuple[Optional[Entity], List[Fact]]:
        """Resolve entity mention and return its canonical definition and all linked facts."""
        entity = self.resolver.resolve(entity_mention)
        if not entity:
            return None, []

        all_facts = self.db.get_all_facts()
        entity_facts = [f for f in all_facts if f.subject.upper() == entity.entity_id.upper()]
        return entity, entity_facts

    def get_entity_relationships(self, entity_mention: str) -> List[Relationship]:
        """Return all topological and functional relationships for the entity."""
        entity = self.resolver.resolve(entity_mention)
        if not entity:
            return []

        all_rels = self.db.get_all_relationships()
        return [r for r in all_rels if r.source_entity.upper() == entity.entity_id.upper() or r.target_entity.upper() == entity.entity_id.upper()]

    def search_facts(self, predicate_pattern: str) -> List[Fact]:
        """Search facts matching a predicate pattern."""
        all_facts = self.db.get_all_facts()
        return [f for f in all_facts if predicate_pattern.lower() in f.predicate.lower()]
