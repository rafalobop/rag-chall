# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's question in natural language.")

class SourceInfo(BaseModel):
    source: str = Field(..., description="The category/source of the referenced content.")

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[SourceInfo]

class DocumentRequest(BaseModel):
    content: str = Field(..., description="Text content to be parsed and indexed.")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional document level metadata.")

class DocumentResponse(BaseModel):
    status: str
    chunks_indexed: int
