import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.infrastructure.chroma_repository import ChromaRepository
from app.infrastructure.openai_service import OpenAIService
from app.domain.entities import Document
from app.use_cases.index_knowledge import IndexKnowledgeUseCase
from app.interfaces.api import router

app = FastAPI(
    title="API de Desafío RAG",
    description="API RAG con guardrails de formato de nivel de producción bajo Arquitectura Limpia.",
    version="1.0.0"
)

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    """Serves a premium, responsive Web UI to interact with the RAG API endpoints."""
    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Galactic RAG Control Center</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            --glass-bg: rgba(30, 41, 59, 0.7);
            --glass-border: rgba(255, 255, 255, 0.08);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-glow: #6366f1;
            --accent-hover: #4f46e5;
            --success: #10b981;
            --error: #f43f5e;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Outfit', sans-serif;
            -webkit-font-smoothing: antialiased;
        }
        
        body {
            background: var(--bg-gradient);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: center;
            padding: 2rem 1rem;
        }

        .container {
            width: 100%;
            max-width: 900px;
            margin-top: 1rem;
        }

        header {
            text-align: center;
            margin-bottom: 2rem;
        }

        header h1 {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(to right, #818cf8, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            letter-spacing: -0.05em;
        }

        header p {
            color: var(--text-secondary);
            font-size: 1.1rem;
        }

        .tabs {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            justify-content: center;
        }

        .tab-btn {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            color: var(--text-secondary);
            padding: 0.75rem 1.5rem;
            border-radius: 9999px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .tab-btn.active {
            background: var(--accent-glow);
            color: var(--text-primary);
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
            border-color: transparent;
        }

        .tab-btn:hover {
            color: var(--text-primary);
            border-color: var(--accent-glow);
        }

        .panel {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 1.5rem;
            padding: 2rem;
            backdrop-filter: blur(16px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
            display: none;
            animation: fadeIn 0.4s ease-out forwards;
        }

        .panel.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #c084fc;
            font-size: 0.95rem;
        }

        .input-group {
            margin-bottom: 1.5rem;
        }

        input[type="text"], textarea {
            width: 100%;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--glass-border);
            border-radius: 0.75rem;
            padding: 1rem;
            color: var(--text-primary);
            font-size: 1rem;
            outline: none;
            transition: border-color 0.3s;
            resize: vertical;
        }

        input[type="text"]:focus, textarea:focus {
            border-color: var(--accent-glow);
        }

        .btn {
            background: var(--accent-glow);
            color: white;
            border: none;
            width: 100%;
            padding: 1rem;
            border-radius: 0.75rem;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s, transform 0.1s;
        }

        .btn:hover {
            background: var(--accent-hover);
        }

        .btn:active {
            transform: scale(0.98);
        }

        .response-card {
            margin-top: 1.5rem;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid var(--glass-border);
            border-radius: 1rem;
            padding: 1.5rem;
            display: none;
        }

        .response-card h3 {
            font-size: 1.1rem;
            margin-bottom: 0.75rem;
            color: var(--success);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .response-text {
            line-height: 1.6;
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }

        .meta-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }

        .badge {
            background: rgba(99, 102, 241, 0.2);
            border: 1px solid rgba(99, 102, 241, 0.4);
            color: #a5b4fc;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .schema-box {
            background: rgba(0, 0, 0, 0.3);
            border-left: 3px solid #c084fc;
            padding: 1rem;
            border-radius: 0.5rem;
            font-family: monospace;
            font-size: 0.85rem;
            margin-bottom: 1.5rem;
            color: #e2e8f0;
            white-space: pre-wrap;
        }

        .footer {
            margin-top: 3rem;
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.85rem;
        }
    </style>
</head>
<body>

    <header>
        <h1>Galactic RAG Control Center</h1>
        <p>Ecosistema de agentes interactivo bajo Arquitectura Limpia</p>
    </header>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('query')">Consultar RAG</button>
        <button class="tab-btn" onclick="switchTab('ingest')">Indexar Conocimiento</button>
    </div>

    <div class="container">
        <!-- RAG QUERY PANEL -->
        <div id="query-panel" class="panel active">
            <label>Estructura del Request Body (POST /api/v1/query):</label>
            <div class="schema-box">{
  "query": "Tu pregunta en lenguaje natural aquí (ej: ¿Qué descubrió Zara?)"
}</div>

            <div class="input-group">
                <label for="query-input">Pregunta en Lenguaje Natural</label>
                <input type="text" id="query-input" placeholder="Escribe tu consulta aquí..." value="¿Qué descubrió Zara en Zenthoria?">
            </div>
            
            <button class="btn" onclick="submitQuery()">Enviar Consulta RAG</button>

            <div id="query-result" class="response-card">
                <h3>🔍 Respuesta de la Base de Datos</h3>
                <p id="query-answer" class="response-text"></p>
                <div>
                    <label style="font-size: 0.8rem; margin-bottom: 0.25rem;">Fuentes Citadas:</label>
                    <div id="query-sources" class="meta-badges"></div>
                </div>
            </div>
        </div>

        <!-- DOCUMENT INGEST PANEL -->
        <div id="ingest-panel" class="panel">
            <label>Estructura del Request Body (POST /api/v1/documents):</label>
            <div class="schema-box">{
  "content": "Categoría: Relato o información de conocimiento...",
  "metadata": {
    "key": "value" // Opcional
  }
}</div>

            <div class="input-group">
                <label for="document-content">Contenido a Indexar</label>
                <textarea id="document-content" rows="6" placeholder="Ficción Espacial: En Zenthoria, los exploradores encontraron..."></textarea>
            </div>

            <button class="btn" onclick="submitDocument()">Indexar Conocimiento</button>

            <div id="ingest-result" class="response-card">
                <h3 id="ingest-title">✅ Estado de Ingestión</h3>
                <p id="ingest-detail" class="response-text"></p>
            </div>
        </div>
    </div>

    <div class="footer">
        Desarrollado bajo In-Chain Agent Protocol (MCP -> Dev -> QA) | RAG Challenge
    </div>

    <script>
        function switchTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.panel').forEach(panel => panel.classList.remove('active'));
            
            if (tab === 'query') {
                document.querySelectorAll('.tab-btn')[0].classList.add('active');
                document.getElementById('query-panel').classList.add('active');
            } else {
                document.querySelectorAll('.tab-btn')[1].classList.add('active');
                document.getElementById('ingest-panel').classList.add('active');
            }
        }

        async function submitQuery() {
            const queryVal = document.getElementById('query-input').value;
            const resCard = document.getElementById('query-result');
            const ansText = document.getElementById('query-answer');
            const sourcesDiv = document.getElementById('query-sources');
            
            resCard.style.display = 'none';
            
            try {
                const response = await fetch('/api/v1/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: queryVal })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    ansText.innerText = data.answer;
                    sourcesDiv.innerHTML = '';
                    
                    if (data.sources && data.sources.length > 0) {
                        data.sources.forEach(src => {
                            const badge = document.createElement('span');
                            badge.className = 'badge';
                            badge.innerText = src.source;
                            sourcesDiv.appendChild(badge);
                        });
                    } else {
                        const badge = document.createElement('span');
                        badge.className = 'badge';
                        badge.style.background = 'rgba(244, 63, 94, 0.2)';
                        badge.style.borderColor = 'rgba(244, 63, 94, 0.4)';
                        badge.style.color = '#fda4af';
                        badge.innerText = 'Ninguna (Fallback)';
                        sourcesDiv.appendChild(badge);
                    }
                    
                    resCard.style.display = 'block';
                } else {
                    alert('Error en la consulta: ' + (data.detail || 'Ocurrió un error.'));
                }
            } catch (err) {
                alert('No se pudo conectar con el servidor: ' + err.message);
            }
        }

        async function submitDocument() {
            const contentVal = document.getElementById('document-content').value;
            const resCard = document.getElementById('ingest-result');
            const detailText = document.getElementById('ingest-detail');
            const titleText = document.getElementById('ingest-title');
            
            resCard.style.display = 'none';
            
            if (!contentVal.trim()) {
                alert('Por favor, ingresa contenido válido.');
                return;
            }
            
            try {
                const response = await fetch('/api/v1/documents', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: contentVal, metadata: {} })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    titleText.innerHTML = '✅ Ingesta Exitosa';
                    titleText.style.color = 'var(--success)';
                    detailText.innerText = `Documento indexado correctamente. Se crearon ${data.chunks_indexed} fragmentos semánticos.`;
                    resCard.style.display = 'block';
                    document.getElementById('document-content').value = '';
                } else {
                    titleText.innerHTML = '❌ Error de Ingesta';
                    titleText.style.color = 'var(--error)';
                    detailText.innerText = data.detail || 'Fallo desconocido.';
                    resCard.style.display = 'block';
                }
            } catch (err) {
                alert('No se pudo conectar con el servidor: ' + err.message);
            }
        }
    </script>
</body>
</html>
"""

# Configuración
CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "data/chroma_db")
KNOWLEDGE_FILE = os.getenv("KNOWLEDGE_FILE", "data/knowledge_base.txt")

# Inicializar los adaptadores de infraestructura
vector_db = ChromaRepository(persist_directory=CHROMA_DIR)
llm_service = OpenAIService()

# Adjuntar los adaptadores al estado de la aplicación
app.state.vector_db = vector_db
app.state.llm_service = llm_service

# Incluir las rutas
app.include_router(router)

@app.on_event("startup")
def startup_populate_db():
    """Puebla la base de datos vectorial con el conocimiento inicial si está vacía."""
    try:
        current_count = vector_db.count()
        print(f"[Startup] Cantidad actual de documentos en la base de datos vectorial: {current_count}")
        
        if current_count == 0:
            if os.path.exists(KNOWLEDGE_FILE):
                print(f"[Startup] Cargando base de conocimientos por defecto desde {KNOWLEDGE_FILE}...")
                with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                
                doc = Document(
                    id="initial_knowledge_base",
                    content=content,
                    metadata={"source_file": "knowledge_base.txt"}
                )
                
                use_case = IndexKnowledgeUseCase(vector_db=vector_db)
                num_chunks = use_case.execute(doc)
                print(f"[Startup] Ingesta completada. Se crearon {num_chunks} fragmentos semánticos.")
            else:
                print(f"[Startup] Advertencia: Archivo de conocimiento no encontrado en {KNOWLEDGE_FILE}")
    except Exception as e:
        print(f"[Startup] No se pudo poblar la base de datos vectorial: {str(e)}")
