from typing import List, Dict, Any
from app.domain.entities import Chunk, RAGResponse
from app.domain.interfaces import IVectorDatabase, ILLMService
from app.use_cases.guardrails import GuardrailValidator

class QueryRAGUseCase:
    """Orquestador para todo el pipeline de generación aumentada por recuperación (RAG)."""

    def __init__(self, vector_db: IVectorDatabase, llm_service: ILLMService, guardrail_validator: GuardrailValidator = None):
        self.vector_db = vector_db
        self.llm_service = llm_service
        self.guardrail = guardrail_validator or GuardrailValidator()

    def execute(self, query_text: str) -> RAGResponse:
        """Ejecuta el pipeline RAG: recupera fragmentos, consulta al LLM, ejecuta guardrails y mapea a la entidad de dominio."""
        # Detectar idioma (heurística simple para pruebas)
        language = self._detect_language(query_text)

        # Recuperar fragmentos relevantes (recupera los 3 principales)
        retrieved_chunks = self.vector_db.query(query_text, limit=3)

        # Generar respuesta desde el LLM (o mock)
        raw_answer = self.llm_service.generate_answer(query_text, retrieved_chunks, language)

        # Ejecutar guardrails para validar y corregir la respuesta
        try:
            validated_answer = self.guardrail.validate_and_correct(raw_answer)
        except ValueError:
            # Si la corrección falla, retornar el mensaje de respaldo
            validated_answer = "La información solicitada sobre ese tema no se encuentra disponible en los registros galácticos 🚫📚."

        # Eliminar duplicados de fuentes de los fragmentos
        sources: List[Dict[str, Any]] = []
        seen_sources = set()
        for chunk in retrieved_chunks:
            src = chunk.metadata.get("source", "General")
            if src not in seen_sources:
                seen_sources.add(src)
                sources.append({"source": src})

        # Si la respuesta es la de respaldo, limpiar las fuentes
        if validated_answer == "La información solicitada sobre ese tema no se encuentra disponible en los registros galácticos 🚫📚.":
            sources = []

        return RAGResponse(
            query=query_text,
            answer=validated_answer,
            sources=sources
        )

    def _detect_language(self, text: str) -> str:
        """Determina si la consulta está en español, inglés o portugués usando palabras clave comunes."""
        text_lower = text.lower()
        
        # Intersección simple de stopwords
        english_words = {"who", "what", "where", "is", "the", "flower", "clock", "hero", "about"}
        portuguese_words = {"quem", "onde", "flor", "relogio", "heroi", "sobre", "uma", "antigo"}
        
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        if words.intersection(english_words):
            return "English"
        elif words.intersection(portuguese_words):
            return "Portuguese"
        else:
            return "Spanish"

# Ayudante para coincidencia de patrones de texto
import re
