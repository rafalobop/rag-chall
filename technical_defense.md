# 🛡️ Technical Defense: Architecture & RAG Decisions (Senior/Staff Level)

This document contains the theoretical defense and architectural decisions that justify the structure and implementation of the RAG Challenge.

---

## 1. Clean Architecture & Layered Separation
Following Clean Architecture, the dependencies point strictly inwards:
- **Domain Layer (`app/domain/`):** Houses pure enterprise rules (`entities.py`) and protocol abstractions (`interfaces.py`). It remains completely untainted by external frameworks (FastAPI, ChromaDB, OpenAI, etc.).
- **Use Cases (`app/use_cases/`):** Contains pure orchestration flows (e.g. `index_knowledge.py` or `query_rag.py`). It coordinates entities to execute the business requirements.
- **Infrastructure Layer (`app/infrastructure/`):** Implements technology-specific adapters (ChromaDB, OpenAI HTTP client). If we need to replace ChromaDB with Qdrant or Pinecone, we only modify this layer, without touching the application core.
- **Interfaces Layer (`app/interfaces/`):** Entrypoints like HTTP controllers (FastAPI) and validation schemas (Pydantic).

---

## 2. Advanced Chunking Strategy: Semantic Paragraph Splitting
Traditional chunking algorithms (like splitters based on a fixed character count) break text arbitrarily, frequently splitting sentences or separating key details from their context, which degrades semantic matching.

- **Logical Domain Context:** Our knowledge base consists of individual stories/records. Splitting by section header (`Section: Text`) ensures each story resides in a single, high-fidelity context.
- **Category Metadata Injection:** By parsing the prefix (e.g., `Ficción Espacial`) and saving it as the chunk's `source` metadata, we enable filtering and clear source tracking.
- **Recursive Overflow Splitter:** When a story exceeds 500 tokens, a recursive separator hierarchy (`\n\n` -> `\n` -> `. ` -> ` `) preserves coherence down to the word level while maintaining an overlap of 50 tokens to bridge narratives.

---

## 3. Hermetic Testing & Offline Capabilities
Production-grade systems must run tests reliably without flaky network calls or consuming paid API credits:
- We abstract database and LLM calls via abstract classes (`IVectorDatabase` and `ILLMService`).
- In testing, we plug in mocks or in-memory repositories. This enables local development and zero-dependency CI runs.
