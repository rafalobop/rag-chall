import os
from fastapi import FastAPI
from app.infrastructure.chroma_repository import ChromaRepository
from app.infrastructure.openai_service import OpenAIService
from app.domain.entities import Document
from app.use_cases.index_knowledge import IndexKnowledgeUseCase
from app.interfaces.api import router

app = FastAPI(
    title="RAG Challenge API",
    description="Production-grade, clean architecture RAG API with formatting guardrails.",
    version="1.0.0"
)

# Configuration
CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "data/chroma_db")
KNOWLEDGE_FILE = os.getenv("KNOWLEDGE_FILE", "data/knowledge_base.txt")

# Initialize infrastructure adapters
vector_db = ChromaRepository(persist_directory=CHROMA_DIR)
llm_service = OpenAIService()

# Attach adapters to app state
app.state.vector_db = vector_db
app.state.llm_service = llm_service

# Include routing
app.include_router(router)

@app.on_event("startup")
def startup_populate_db():
    """Populates the vector store with initial knowledge if it is empty."""
    try:
        current_count = vector_db.count()
        print(f"[Startup] Current vector store document count: {current_count}")
        
        if current_count == 0:
            if os.path.exists(KNOWLEDGE_FILE):
                print(f"[Startup] Loading default knowledge base from {KNOWLEDGE_FILE}...")
                with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                
                doc = Document(
                    id="initial_knowledge_base",
                    content=content,
                    metadata={"source_file": "knowledge_base.txt"}
                )
                
                use_case = IndexKnowledgeUseCase(vector_db=vector_db)
                num_chunks = use_case.execute(doc)
                print(f"[Startup] Ingestion complete. Created {num_chunks} semantic chunks.")
            else:
                print(f"[Startup] Warning: Knowledge file not found at {KNOWLEDGE_FILE}")
    except Exception as e:
        print(f"[Startup] Failed to populate vector store: {str(e)}")
