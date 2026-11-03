"""
Base classes and interfaces for document ingestion in the Aegis system.
"""

from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Any
from storage.models import Document, DocumentChunk


class BaseExtractor(ABC):
    """Abstract base extractor interface for all file modalities."""

    @abstractmethod
    def extract(self, filepath: str, filename: str, doc_metadata: Dict[str, Any]) -> Tuple[Document, List[DocumentChunk]]:
        """
        Extract document metadata and granular chunks.
        
        Args:
            filepath: Absolute or relative path to source file.
            filename: Normalized filename.
            doc_metadata: Inferred metadata (trust level, doc_type, etc.)
            
        Returns:
            Tuple of (Document, List[DocumentChunk])
        """
        pass

