from abc import ABC, abstractmethod
from typing import List
from app.domain.entities import Chunk, Document

class IVectorDatabase(ABC):
    """Abstract interface for storing and querying vector embeddings."""

    @abstractmethod
    def add_chunks(self, chunks: List[Chunk]) -> None:
        """Embeds and persists chunks in the vector database."""
        pass

    @abstractmethod
    def query(self, query_text: str, limit: int = 3) -> List[Chunk]:
        """Performs semantic search to find chunks matching the query."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clears all stored chunks from the database (mainly for testing/clean restarts)."""
        pass


class ILLMService(ABC):
    """Abstract interface for interacting with Large Language Models."""

    @abstractmethod
    def generate_answer(self, query: str, context: List[Chunk], language: str) -> str:
        """Generates a response from the LLM based on context chunks and detected language.
        
        Args:
            query: User's question.
            context: Chunks matching the user query.
            language: The language detected from the user's query.
            
        Returns:
            The raw text answer conforming to syntax and style guidelines.
        """
        pass
