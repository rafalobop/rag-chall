# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., description="La pregunta del usuario en lenguaje natural.")

class SourceInfo(BaseModel):
    source: str = Field(..., description="La categoría/fuente del contenido referenciado.")

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[SourceInfo]

class DocumentRequest(BaseModel):
    content: str = Field(..., description="El contenido de texto que será procesado e indexado.")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadatos opcionales a nivel de documento.")

class DocumentResponse(BaseModel):
    status: str
    chunks_indexed: int
