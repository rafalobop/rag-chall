# 💻 Agent Dev Report: Code Decisions & Chunking Strategy

This report details the core software engineering decisions made during Phase 1.

---

## 🔍 Architecture & Patterns

1. **Clean Architecture (Domain-Driven Core):**
   - All domain rules are declared in `app/domain`. Dataclasses are read-only (`frozen=True`) to maintain purity and prevent side-effects.
   - External dependencies (like database clients or HTTP wrappers) never leak into the Use Cases or Entities.

2. **Estrategia de Chunking: Semantic Paragraph Splitting:**
   - Raw files are segmented by line. Each line adheres to `[Sección]: [Contenido]`.
   - The parser splits these parts using a single split at `:` to separate the section header (e.g. `Ficción Espacial`) from the story.
   - The category is injected into `Chunk.metadata["source"]` so the LLM knows the source category.

3. **Control de Tokens:**
   - **Limit:** 500 tokens.
   - **Reasoning:** A typical query context context window can handle several paragraphs. Standardizing chunks to <= 500 tokens ensures we can provide multiple high-relevance chunks to the LLM context window without running out of tokens or causing "lost in the middle" retrieval quality drops.
   - **Fallback Splitting:** If a section exceeds 500 tokens, it goes through a recursive token-aware splitter that breaks by paragraphs (`\n\n`), newlines (`\n`), sentences (`. `), and words (` `), incorporating a `50` token overlap to avoid cut-off narratives at boundaries.
