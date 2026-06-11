# 🏛️ Agent MCP & Project Manager Report: Architecture & Planning

This document defines the system configuration, runtime environments, vector database settings, API ports, and the feature development pipeline managed by the Project Manager Agent.

---

## ⚙️ Environment and Tools Configuration

- **Runtime Environment:** Python 3.10+
- **API Framework:** FastAPI
- **Web Server:** Uvicorn (running on Port `8000`)
- **Vector Database:** ChromaDB (local persistent storage via SQLite stored in `data/chroma_db`)
- **Key Dependencies:**
  - `fastapi` & `uvicorn` (REST API layer)
  - `pydantic` (Data transfer validation)
  - `chromadb` (Semantic search / Vector DB)
  - `openai` (LLM communication)
  - `pytest` & `pytest-mock` (Offline test runner)
  - `tiktoken` (Exact token counting helper)

---

## 🛠️ Vector Database Configuration

We follow the **Repository Pattern** decoupled via `IVectorDatabase` in the domain layer. 

- **Local Development / CI Persistence:** Disk-persisted SQLite db.
- **Production Extension:** The interface permits dropping in Qdrant/Pinecone classes with no domain alterations.
- **Distance Metric:** Cosine similarity (`cosine`).

---

## 📋 Project Manager Feature Backlog (JSON Specification)

```json
[
  {
    "id": "FEAT-01",
    "feature": "Clean Architecture Domain & Interfaces",
    "descripcion": "Establecer la estructura base del proyecto implementando entidades de dominio puras e interfaces para desacoplar base de datos vectorial y servicios de LLM.",
    "alcance": "Definición de entidades (Document, Chunk, QueryResult, RAGResponse) e interfaces abstractas (IVectorDatabase, ILLMService).",
    "agente_ejecutor": "Agente Dev",
    "agente_probador": "Agente QA",
    "DoD": "Entidades e interfaces declaradas en app/domain sin dependencias de frameworks externos. Importaciones libres de errores sintácticos."
  },
  {
    "id": "FEAT-02",
    "feature": "Semantic Paragraph Splitting (Parser)",
    "descripcion": "Desarrollar la estrategia de chunking semántico por párrafos basados en la estructura del documento oficial, con control de tamaño y solapamiento de tokens.",
    "alcance": "Algoritmo de parsing que extrae metadatos de categoría y subdivide relatos que excedan 500 tokens usando un splitter recursivo secundario.",
    "agente_ejecutor": "Agente Dev",
    "agente_probador": "Agente QA",
    "DoD": "Prueba unitaria offline exitosa donde textos > 500 tokens se fragmentan en porciones más pequeñas preservando el metadato 'source' correcto."
  },
  {
    "id": "FEAT-03",
    "feature": "Mock VectorDB and Offline Validation",
    "descripcion": "Crear adaptadores mock para posibilitar ejecuciones de prueba offline y validar la consistencia lógica de las capas de negocio sin depender de APIs de pago.",
    "alcance": "Implementación de ChromaRepository mockeada o en memoria temporal para verificar la ingesta y recuperación.",
    "agente_ejecutor": "Agente Dev / QA",
    "agente_probador": "Agente QA",
    "DoD": "Suite de pruebas ejecutada al 100% de éxito en modo offline local sin credenciales de OpenAI."
  }
]
```
