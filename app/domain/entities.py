from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass(frozen=True)
class Document:
    """Representa un documento de texto indexado."""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Chunk:
    """Representa un fragmento de un documento procesado semánticamente."""
    id: str
    document_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class QueryResult:
    """Representa el resultado de la búsqueda semántica que coincide con la consulta."""
    query: str
    matched_chunks: List[Chunk] = field(default_factory=list)

@dataclass(frozen=True)
class RAGResponse:
    """Representa la respuesta final generada por el LLM."""
    query: str
    answer: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
