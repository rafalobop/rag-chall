import uuid
import re
from typing import List, Dict, Any
from app.domain.entities import Chunk, Document
from app.domain.interfaces import IVectorDatabase

def count_tokens(text: str) -> int:
    """Función de ayuda para contar o estimar la cantidad de tokens usando tiktoken o un estimador simple."""
    try:
        # pyrefly: ignore [missing-import]
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except ImportError:
        # Estimación de respaldo: 1 palabra ~ 1.3 tokens
        return int(len(text.split()) * 1.3)


def split_text_recursively(text: str, max_tokens: int = 500, overlap_tokens: int = 50) -> List[str]:
    """Divide un texto recursivamente en segmentos más pequeños que quepan dentro de max_tokens."""
    if count_tokens(text) <= max_tokens:
        return [text]

    separators = ["\n\n", "\n", ". ", " ", ""]

    def _split(txt: str, separators_list: List[str]) -> List[str]:
        if count_tokens(txt) <= max_tokens:
            return [txt]
        if not separators_list:
            # Respaldo por caracteres si no quedan separadores
            char_limit = int(max_tokens * 3.5)
            char_overlap = int(overlap_tokens * 3.5)
            chunks = []
            start = 0
            while start < len(txt):
                end = min(start + char_limit, len(txt))
                chunks.append(txt[start:end])
                if end == len(txt):
                    break
                start += char_limit - char_overlap
            return chunks

        sep = separators_list[0]
        parts = txt.split(sep)
        
        chunks = []
        current_chunk = []
        current_tokens = 0

        for part in parts:
            part_txt = part + (sep if sep != "" else "")
            part_tokens = count_tokens(part_txt)

            if part_tokens > max_tokens:
                # Vaciar el acumulador actual
                if current_chunk:
                    chunks.append(sep.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                # Dividir la parte de gran tamaño con los siguientes separadores
                sub_parts = _split(part, separators_list[1:])
                chunks.extend(sub_parts)
            else:
                # Comprobar si cabe
                if current_tokens + part_tokens > max_tokens:
                    if current_chunk:
                        chunks.append(sep.join(current_chunk))
                    # Retener algo de solapamiento
                    overlap_chunk = []
                    overlap_t = 0
                    for p in reversed(current_chunk):
                        p_t = count_tokens(p + sep)
                        if overlap_t + p_t <= overlap_tokens:
                            overlap_chunk.insert(0, p)
                            overlap_t += p_t
                        else:
                            break
                    current_chunk = overlap_chunk
                    current_tokens = overlap_t

                current_chunk.append(part)
                current_tokens += part_tokens

        if current_chunk:
            chunks.append(sep.join(current_chunk))

        return chunks

    return _split(text, separators)


class IndexKnowledgeUseCase:
    """Orquesta la lectura de documentos, el chunking semántico por párrafos y la indexación en la base de datos."""

    def __init__(self, vector_db: IVectorDatabase, max_tokens: int = 500, overlap_tokens: int = 50):
        self.vector_db = vector_db
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def execute(self, document: Document) -> int:
        """Procesa el documento, extrae categorías, controla límites de tokens e indexa en la base de datos vectorial."""
        chunks = self._parse_semantic_chunks(document)
        if chunks:
            self.vector_db.add_chunks(chunks)
        return len(chunks)

    def _parse_semantic_chunks(self, document: Document) -> List[Chunk]:
        """Divide el contenido del documento por líneas/relatos, extrayendo los títulos como fuentes."""
        chunks: List[Chunk] = []
        lines = document.content.strip().split("\n")

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Detección de formato estándar: "Categoría: Contenido"
            if ":" in line_str:
                source, content = line_str.split(":", 1)
                source = source.strip()
                content = content.strip()
            else:
                source = "General"
                content = line_str

            # Comprobar si la parte de contenido supera el límite de tokens
            content_tokens = count_tokens(content)
            if content_tokens > self.max_tokens:
                sub_segments = split_text_recursively(content, self.max_tokens, self.overlap_tokens)
                for idx, sub_txt in enumerate(sub_segments):
                    chunk_id = f"{document.id}_{source}_{idx}_{uuid.uuid4().hex[:8]}"
                    chunks.append(Chunk(
                        id=chunk_id,
                        document_id=document.id,
                        content=f"{source}: {sub_txt}",
                        metadata={"source": source, "part": idx}
                    ))
            else:
                chunk_id = f"{document.id}_{source}_{uuid.uuid4().hex[:8]}"
                chunks.append(Chunk(
                    id=chunk_id,
                    document_id=document.id,
                    content=line_str,
                    metadata={"source": source}
                ))

        return chunks
