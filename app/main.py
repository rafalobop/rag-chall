import os
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from app.infrastructure.chroma_repository import ChromaRepository
from app.infrastructure.openai_service import OpenAIService
from app.domain.entities import Document
from app.use_cases.index_knowledge import IndexKnowledgeUseCase
from app.interfaces.api import router

app = FastAPI(
    title="API de Desafío RAG",
    description="API RAG con guardrails de formato de nivel de producción bajo Arquitectura Limpia.",
    version="1.0.0"
)

# Configuración
CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "data/chroma_db")
KNOWLEDGE_FILE = os.getenv("KNOWLEDGE_FILE", "data/knowledge_base.txt")

# Inicializar los adaptadores de infraestructura
vector_db = ChromaRepository(persist_directory=CHROMA_DIR)
llm_service = OpenAIService()

# Adjuntar los adaptadores al estado de la aplicación
app.state.vector_db = vector_db
app.state.llm_service = llm_service

# Incluir las rutas
app.include_router(router)

@app.on_event("startup")
def startup_populate_db():
    """Puebla la base de datos vectorial con el conocimiento inicial si está vacía."""
    try:
        current_count = vector_db.count()
        print(f"[Startup] Cantidad actual de documentos en la base de datos vectorial: {current_count}")
        
        if current_count == 0:
            if os.path.exists(KNOWLEDGE_FILE):
                print(f"[Startup] Cargando base de conocimientos por defecto desde {KNOWLEDGE_FILE}...")
                with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                
                doc = Document(
                    id="initial_knowledge_base",
                    content=content,
                    metadata={"source_file": "knowledge_base.txt"}
                )
                
                use_case = IndexKnowledgeUseCase(vector_db=vector_db)
                num_chunks = use_case.execute(doc)
                print(f"[Startup] Ingesta completada. Se crearon {num_chunks} fragmentos semánticos.")
            else:
                print(f"[Startup] Advertencia: Archivo de conocimiento no encontrado en {KNOWLEDGE_FILE}")
    except Exception as e:
        print(f"[Startup] No se pudo poblar la base de datos vectorial: {str(e)}")
