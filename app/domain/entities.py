from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass(frozen=True)
class Document:
    """Represents an ingested text document."""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Chunk:
    """Represents a segment of a Document parsed semantically."""
    id: str
    document_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class QueryResult:
    """Represents the semantic retrieval results matching a query."""
    query: str
    matched_chunks: List[Chunk] = field(default_factory=list)

@dataclass(frozen=True)
class RAGResponse:
    """Represents the final formulated answer from the LLM."""
    query: str
    answer: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
