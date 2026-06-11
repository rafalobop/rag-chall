# 🚀 API de Desafío RAG (Clean Architecture)

Este proyecto consiste en una API RAG (Retrieval-Augmented Generation) de grado de producción, diseñada bajo los principios de **Arquitectura Limpia (Clean Architecture)** y **SOLID**. El sistema responde a consultas de usuarios basándose en una base de conocimientos indexada semánticamente, garantizando estrictas restricciones de formato, idioma y estilo corporativo a través de una capa de validación inteligente (Guardrails).

---

## 🏛️ Estructura del Proyecto

El código está organizado siguiendo un flujo de control concéntrico hacia el dominio (independiente de frameworks y tecnologías externas):

```
app/
├── domain/                    # Capa de Dominio (Entidades de negocio y protocolos puros)
│   ├── entities.py            # Dataclasses: Document, Chunk, QueryResult, RAGResponse
│   └── interfaces.py          # Interfaces abstractas: IVectorDatabase, ILLMService
│
├── use_cases/                 # Capa de Aplicación / Casos de Uso (Reglas de negocio aplicadas)
│   ├── index_knowledge.py     # Parser semántico por párrafos y control de tokens (500 tokens)
│   ├── query_rag.py           # Orquestador del flujo RAG
│   └── guardrails.py          # Validador y auto-corrector de formato
│
├── infrastructure/            # Capa de Infraestructura (Adaptadores de tecnología)
│   ├── chroma_repository.py   # Repositorio concreto de ChromaDB (SQLite local)
│   └── openai_service.py      # Servicio OpenAI con soporte de Mock offline multilingüe
│
└── interfaces/                # Capa de Presentación (Controladores FastAPI y validación HTTP)
    ├── api.py                 # Endpoints FastAPI
    └── schemas.py             # Modelos de validación de datos (Pydantic)
```

---

## 🛠️ Requisitos Previos

* Python 3.10 o superior.
* Docker (opcional, para ejecución en contenedores).

---

## 🚀 Instalación y Configuración Local

1. **Clonar el repositorio y situarse en la carpeta:**
   ```bash
   git clone https://github.com/rafalobop/rag-chall.git
   cd rag-chall
   ```

2. **Crear e inicializar un entorno virtual:**
   ```bash
   python -m venv .venv
   # En Windows (Powershell):
   .venv\Scripts\Activate.ps1
   # En Linux/macOS:
   source .venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Variables de entorno:**
   Crea un archivo `.env` en la raíz del proyecto basándote en el archivo `.env.example`:
   ```bash
   # Si deseas utilizar el modelo de producción real de OpenAI, coloca tu API key.
   # Si lo dejas vacío, el sistema funcionará al 100% de manera autónoma en modo MOCK offline.
   OPENAI_API_KEY=tu_api_key_de_openai
   CHROMA_PERSIST_DIR=data/chroma_db
   KNOWLEDGE_FILE=data/knowledge_base.txt
   ```

5. **Iniciar la aplicación:**
   ```bash
   # En Windows (Powershell):
   $env:PYTHONPATH="."
   python -m uvicorn app.main:app --reload

   # En Linux/macOS:
   PYTHONPATH=. python -m uvicorn app.main:app --reload
   ```
   La API estará disponible en `http://localhost:8000`. Puedes ingresar a la documentación interactiva en `http://localhost:8000/docs`.

---

## 🐳 Ejecución con Docker

Para construir y levantar el entorno totalmente contenerizado y portable:

1. **Construir la imagen de Docker (Multi-stage build):**
   ```bash
   docker build -t rag-challenge-api .
   ```

2. **Correr el contenedor exponiendo el puerto 8000:**
   ```bash
   docker run -p 8000:8000 -e OPENAI_API_KEY="tu_api_key" rag-challenge-api
   ```
   *(Nota: Puedes omitir `-e OPENAI_API_KEY` para iniciar el contenedor en modo mock offline)*.

---

## 🧪 Ejecución de Pruebas Automáticas

La suite de pruebas contiene tests unitarios y de integración completos que validan el chunking semántico por tokens, las validaciones de guardrails, los flujos multilingües y las respuestas de fallback.

Ejecuta el siguiente comando para correr los tests:
```bash
# Con el entorno virtual activo:
python -m unittest discover tests
```

---

## 📋 Pruebas Manuales con Postman

En la raíz del proyecto se incluye el archivo `postman_collection.json`. Puedes importarlo directamente en Postman para probar todos los casos de uso:

1. **Ingestar un documento dinámico (`POST /api/v1/documents`):**
   Envía un texto estructurado en el body (ej: `"Ficción Espacial: En Zenthoria..."`) para indexarlo al instante.
2. **Consulta RAG - Español (`POST /api/v1/query`):**
   Pregunta por *Zara* o la *Flor Mágica* en español y recibe respuestas validadas por los guardrails corporativos.
3. **Consulta RAG - Inglés o Portugués:**
   Comprueba el multilingüismo dinámico haciendo consultas en estos idiomas (ej: *"Tell me about the magic flower"*).
4. **Consulta RAG - Fallback:**
   Pregunta algo fuera de contexto (ej: recetas de cocina) y comprueba el retorno del mensaje por defecto de los registros galácticos.
