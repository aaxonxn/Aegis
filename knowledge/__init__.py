from knowledge.entity_resolution import EntityResolver, CANONICAL_ENTITIES
from knowledge.conflict_manager import ConflictManager, TRUST_WEIGHTS
from knowledge.fact_extractor import build_knowledge_base

__all__ = [
    "EntityResolver",
    "CANONICAL_ENTITIES",
    "ConflictManager",
    "TRUST_WEIGHTS",
    "build_knowledge_base"
]

