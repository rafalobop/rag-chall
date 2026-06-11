import os
from typing import List, Dict, Any
# pyrefly: ignore [missing-import]
import chromadb
from app.domain.entities import Chunk
from app.domain.interfaces import IVectorDatabase

class ChromaRepository(IVectorDatabase):
    """Adaptador de infraestructura concreto para ChromaDB."""

    def __init__(self, persist_directory: str = None):
        """Inicializa el cliente de ChromaDB. Usa EphemeralClient si persist_directory es None."""
        if persist_directory:
            # Crear directorios si es necesario
            os.makedirs(persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.EphemeralClient()
            
        self.collection = self.client.get_or_create_collection(
            name="rag_knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Chunk]) -> None:
        """Guarda los fragmentos y sus metadatos en ChromaDB."""
        if not chunks:
            return

        ids = [c.id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = []
        for c in chunks:
            # Copiamos y enriquecemos los metadatos con el id del documento
            meta = dict(c.metadata)
            meta["document_id"] = c.document_id
            metadatas.append(meta)

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def query(self, query_text: str, limit: int = 3) -> List[Chunk]:
        """Consulta la colección de ChromaDB por los vecinos más cercanos usando distancia coseno."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=limit
        )

        chunks: List[Chunk] = []
        if not results or not results["ids"] or len(results["ids"][0]) == 0:
            return chunks

        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        for chunk_id, doc, meta in zip(ids, documents, metadatas):
            doc_id = meta.get("document_id", "unknown")
            chunks.append(Chunk(
                id=chunk_id,
                document_id=doc_id,
                content=doc,
                metadata=meta
            ))

        return chunks

    def count(self) -> int:
        """Retorna la cantidad de documentos almacenados en la colección."""
        return self.collection.count()

    def clear(self) -> None:
        """Elimina y vuelve a construir la colección."""
        try:
            self.client.delete_collection("rag_knowledge_base")
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name="rag_knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )
