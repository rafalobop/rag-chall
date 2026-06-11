from abc import ABC, abstractmethod
from typing import List
from app.domain.entities import Chunk, Document

class IVectorDatabase(ABC):
    """Interfaz abstracta para almacenar y consultar embeddings vectoriales."""

    @abstractmethod
    def add_chunks(self, chunks: List[Chunk]) -> None:
        """Vectoriza y persiste fragmentos en la base de datos vectorial."""
        pass

    @abstractmethod
    def query(self, query_text: str, limit: int = 3) -> List[Chunk]:
        """Realiza una búsqueda semántica para encontrar fragmentos que coincidan con la consulta."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Retorna la cantidad de fragmentos almacenados en la colección."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Limpia todos los fragmentos almacenados en la base de datos (para pruebas o reinicios limpios)."""
        pass


class ILLMService(ABC):
    """Interfaz abstracta para interactuar con modelos de lenguaje de gran tamaño (LLM)."""

    @abstractmethod
    def generate_answer(self, query: str, context: List[Chunk], language: str) -> str:
        """Genera una respuesta desde el LLM basada en los fragmentos de contexto y el idioma detectado.
        
        Args:
            query: Pregunta del usuario.
            context: Fragmentos que coinciden con la consulta del usuario.
            language: El idioma detectado de la consulta del usuario.
            
        Returns:
            La respuesta en texto plano que cumple con las directrices de sintaxis y estilo.
        """
        pass
