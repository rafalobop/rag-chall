import unittest
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
from app.main import app
from app.infrastructure.chroma_repository import ChromaRepository
from app.infrastructure.openai_service import OpenAIService

class TestAPIIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Reemplazar repositorios con versiones efímeras/mock para las pruebas
        cls.test_db = ChromaRepository(persist_directory=None) # Cliente efímero
        cls.test_llm = OpenAIService(api_key=None) # Corre en modo Mock
 
        # Inyectar en el estado de la aplicación
        app.state.vector_db = cls.test_db
        app.state.llm_service = cls.test_llm
        
        cls.client = TestClient(app)

    def setUp(self):
        self.test_db.clear()

    def test_document_indexing_and_query_flow(self):
        # 1. Indexar un documento dinámicamente
        doc_payload = {
            "content": "Ficción Espacial: En el planeta Zenthoria, Zara descubrió el artefacto místico que brinda armonía.",
            "metadata": {"origin": "test-suite"}
        }
        res_doc = self.client.post("/api/v1/documents", json=doc_payload)
        self.assertEqual(res_doc.status_code, 200)
        self.assertEqual(res_doc.json()["status"], "success")
        self.assertEqual(res_doc.json()["chunks_indexed"], 1)

        # 2. Consultar el índice
        query_payload = {"query": "Tell me about Zara in Zenthoria"}
        res_query = self.client.post("/api/v1/query", json=query_payload)
        self.assertEqual(res_query.status_code, 200)
        
        data = res_query.json()
        self.assertEqual(data["query"], "Tell me about Zara in Zenthoria")
        # Verificar reglas de formato en la respuesta:
        # Exactamente una oración (contiene un solo punto)
        self.assertEqual(data["answer"].count("."), 1)
        # Termina con un punto
        self.assertTrue(data["answer"].endswith("."))
        # Escrito en inglés (detectado inglés a partir del stopword "about/in")
        self.assertIn("Zara", data["answer"])
        self.assertIn("Zenthoria", data["answer"])
        self.assertIn("explorer", data["answer"].lower())
        # Las fuentes contienen Ficción Espacial
        self.assertEqual(data["sources"], [{"source": "Ficción Espacial"}])

    def test_fallback_out_of_context(self):
        # Consultar por algo completamente irrelevante
        query_payload = {"query": "What is the recipe for chocolate chip cookies?"}
        res_query = self.client.post("/api/v1/query", json=query_payload)
        self.assertEqual(res_query.status_code, 200)
        
        data = res_query.json()
        self.assertEqual(data["answer"], "La información solicitada sobre ese tema no se encuentra disponible en los registros galácticos 🚫📚.")
        self.assertEqual(data["sources"], [])


if __name__ == "__main__":
    unittest.main()
