import unittest
from typing import List
from app.domain.entities import Chunk, Document
from app.domain.interfaces import IVectorDatabase
from app.use_cases.index_knowledge import IndexKnowledgeUseCase, count_tokens

class MockVectorDB(IVectorDatabase):
    def __init__(self):
        self.chunks: List[Chunk] = []

    def add_chunks(self, chunks: List[Chunk]) -> None:
        self.chunks.extend(chunks)

    def query(self, query_text: str, limit: int = 3) -> List[Chunk]:
        return self.chunks[:limit]

    def count(self) -> int:
        return len(self.chunks)

    def clear(self) -> None:
        self.chunks.clear()


class TestSemanticChunking(unittest.TestCase):
    def setUp(self):
        self.db = MockVectorDB()

    def test_semantic_splitting_correct_sources(self):
        # Preparación de documentos
        content = (
            "Ficción Espacial: En la lejana galaxia de Zenthoria.\n"
            "Naturaleza Deslumbrante: La flor mágica Luz de Luna florece de noche."
        )
        doc = Document(id="doc1", content=content)
        
        use_case = IndexKnowledgeUseCase(vector_db=self.db, max_tokens=500)
        num_chunks = use_case.execute(doc)
        
        self.assertEqual(num_chunks, 2)
        self.assertEqual(self.db.chunks[0].metadata["source"], "Ficción Espacial")
        self.assertEqual(self.db.chunks[1].metadata["source"], "Naturaleza Deslumbrante")
        self.assertIn("Ficción Espacial: ", self.db.chunks[0].content)

    def test_token_overflow_splitting(self):
        content = "Ficción Tecnológica: Esta historia es extremadamente larga y sobrepasará el límite establecido."
        doc = Document(id="doc2", content=content)
        
        # Ajustar max_tokens a un número pequeño (ej. 5 tokens) para disparar el divisor recursivo
        use_case = IndexKnowledgeUseCase(vector_db=self.db, max_tokens=5, overlap_tokens=1)
        num_chunks = use_case.execute(doc)
        
        # Debería dividirse en múltiples fragmentos
        self.assertGreater(num_chunks, 1)
        for chunk in self.db.chunks:
            self.assertEqual(chunk.metadata["source"], "Ficción Tecnológica")
            self.assertIn("part", chunk.metadata)
            # Verificar que cada fragmento tenga el prefijo correcto de su categoría/source
            self.assertTrue(chunk.content.startswith("Ficción Tecnológica: "))


if __name__ == "__main__":
    unittest.main()
