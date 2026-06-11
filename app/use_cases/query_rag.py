from typing import List, Dict, Any
from app.domain.entities import Chunk, RAGResponse
from app.domain.interfaces import IVectorDatabase, ILLMService
from app.use_cases.guardrails import GuardrailValidator

class QueryRAGUseCase:
    """Orchestrator for the entire Retrieval-Augmented Generation (RAG) pipeline."""

    def __init__(self, vector_db: IVectorDatabase, llm_service: ILLMService, guardrail_validator: GuardrailValidator = None):
        self.vector_db = vector_db
        self.llm_service = llm_service
        self.guardrail = guardrail_validator or GuardrailValidator()

    def execute(self, query_text: str) -> RAGResponse:
        """Executes RAG pipeline: retrieves chunks, queries LLM, runs guardrails, and maps to entity."""
        # Detect language (simple heuristics for demo/testing)
        language = self._detect_language(query_text)

        # Retrieve relevant chunks (retrieve top 3)
        retrieved_chunks = self.vector_db.query(query_text, limit=3)

        # Generate answer from LLM (or mock)
        raw_answer = self.llm_service.generate_answer(query_text, retrieved_chunks, language)

        # Run guardrails to validate and correct response
        try:
            validated_answer = self.guardrail.validate_and_correct(raw_answer)
        except ValueError:
            # If correction fails, return the fallback message
            validated_answer = "La información solicitada sobre ese tema no se encuentra disponible en los registros galácticos 🚫📚."

        # Deduplicate sources from chunks
        sources: List[Dict[str, Any]] = []
        seen_sources = set()
        for chunk in retrieved_chunks:
            src = chunk.metadata.get("source", "General")
            if src not in seen_sources:
                seen_sources.add(src)
                sources.append({"source": src})

        # If answer is the fallback, clear sources
        if validated_answer == "La información solicitada sobre ese tema no se encuentra disponible en los registros galácticos 🚫📚.":
            sources = []

        return RAGResponse(
            query=query_text,
            answer=validated_answer,
            sources=sources
        )

    def _detect_language(self, text: str) -> str:
        """Determines if query is in Spanish, English, or Portuguese using common stopwords."""
        text_lower = text.lower()
        
        # Simple stopword intersection
        english_words = {"who", "what", "where", "is", "the", "flower", "clock", "hero", "about"}
        portuguese_words = {"quem", "onde", "flor", "relogio", "heroi", "sobre", "uma", "antigo"}
        
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        if words.intersection(english_words):
            return "English"
        elif words.intersection(portuguese_words):
            return "Portuguese"
        else:
            return "Spanish"

# Helper for text pattern matching
import re
