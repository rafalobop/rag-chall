import os
from typing import List, Dict, Any
# pyrefly: ignore [missing-import]
import chromadb
from app.domain.entities import Chunk
from app.domain.interfaces import IVectorDatabase

class ChromaRepository(IVectorDatabase):
    """Concrete Infrastructure Adapter for ChromaDB."""

    def __init__(self, persist_directory: str = None):
        """Initializes ChromaDB client. Uses EphemeralClient if persist_directory is None."""
        if persist_directory:
            # Create directories if needed
            os.makedirs(persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.EphemeralClient()
            
        self.collection = self.client.get_or_create_collection(
            name="rag_knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Chunk]) -> None:
        """Saves chunks and metadata to ChromaDB."""
        if not chunks:
            return

        ids = [c.id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = []
        for c in chunks:
            # We copy and enrich metadata with document_id
            meta = dict(c.metadata)
            meta["document_id"] = c.document_id
            metadatas.append(meta)

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def query(self, query_text: str, limit: int = 3) -> List[Chunk]:
        """Queries ChromaDB collection for nearest neighbors using cosine distance."""
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
        """Returns the number of stored documents in the collection."""
        return self.collection.count()

    def clear(self) -> None:
        """Deletes and rebuilds the collection."""
        try:
            self.client.delete_collection("rag_knowledge_base")
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name="rag_knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )
