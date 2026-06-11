import uuid
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Request, HTTPException
from app.interfaces.schemas import QueryRequest, QueryResponse, DocumentRequest, DocumentResponse
from app.domain.entities import Document
from app.use_cases.query_rag import QueryRAGUseCase
from app.use_cases.index_knowledge import IndexKnowledgeUseCase

router = APIRouter(prefix="/api/v1")

@router.post("/documents", response_model=DocumentResponse)
async def create_document(request: Request, doc_req: DocumentRequest):
    """Indexa un nuevo documento dinámicamente en el almacenamiento vectorial."""
    try:
        vector_db = request.app.state.vector_db
        use_case = IndexKnowledgeUseCase(vector_db=vector_db)
        
        # Instanciar Document del dominio
        doc_id = str(uuid.uuid4())
        document = Document(
            id=doc_id,
            content=doc_req.content,
            metadata=doc_req.metadata or {}
        )
        
        num_chunks = use_case.execute(document)
        return DocumentResponse(status="success", chunks_indexed=num_chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo indexar el documento: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def query_rag(request: Request, query_req: QueryRequest):
    """Procesa una consulta de usuario a través de todo el pipeline RAG."""
    try:
        vector_db = request.app.state.vector_db
        llm_service = request.app.state.llm_service
        
        use_case = QueryRAGUseCase(vector_db=vector_db, llm_service=llm_service)
        result = use_case.execute(query_req.query)
        
        return QueryResponse(
            query=result.query,
            answer=result.answer,
            sources=[{"source": s["source"]} for s in result.sources]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falló la ejecución de la consulta: {str(e)}")
