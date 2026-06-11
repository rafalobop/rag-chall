# 🧪 Agent QA Report: Verification & Validation Matrix

This document outlines the testing strategy, test cases, and quality checks performed on the RAG system core.

---

## 📋 Test Matrix

We validate two main aspects: **Formatting Constraints (Guardrails)** and **Retrieval Reliability**.

| Test ID | Test Category | Input Description | Expected Behavior | Status |
|---|---|---|---|---|
| **QA-01** | Parsing Semántico | `Ficción Espacial: ...` | Parsed into source=`Ficción Espacial`. Metadata contains `source`. | **PASSED** |
| **QA-02** | Token Control (Large Chunk) | Story exceeding 500 tokens | Subdivided into multiple chunks with overlap. Metadata includes `part` index. | **PASSED** |
| **QA-03** | Format Constraint | LLM Raw response | Exactly 1 sentence (ends with `.`), contains at least one emoji, written in 3rd person. | **PASSED** |
| **QA-04** | Fallback Rule | Out-of-bounds query | Returns: *"La información solicitada sobre ese tema no se encuentra disponible en los registros galácticos 🚫📚."* | **PASSED** |

---

## 🔍 Test Data Queries

The knowledge base will be tested against the following entities:
1. **Zara (Ficción Espacial):** Checks if the query retrieves information from `Zenthoria` and returns `source: Ficción Espacial`.
2. **Emma (Cuento Corto):** Checks if retrieval matches the old clock and returns `source: Cuento Corto`.
3. **Flor Mágica (Naturaleza Deslumbrante):** Checks if retrieval matches "Luz de Luna" and returns `source: Naturaleza Deslumbrante`.
