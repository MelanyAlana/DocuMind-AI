from __future__ import annotations

import hashlib
import json
from pathlib import Path

import faiss
import numpy as np

from .chunker import split_pages
from .config import VECTORSTORE_DIR, ensure_directories
from .embeddings import embed_documents, embed_query
from .pdf_loader import extract_pages


class DocumentIndex:
    def __init__(self, index: faiss.Index, chunks: list[dict]):
        self.index, self.chunks = index, chunks

    def search(self, query: str, top_k: int) -> list[dict]:
        vector = embed_query(query).reshape(1, -1)
        scores, ids = self.index.search(vector, min(top_k, len(self.chunks)))
        return [{**self.chunks[i], "score": float(score)} for score, i in zip(scores[0], ids[0]) if i >= 0]


def build_index(chunks: list[dict]) -> DocumentIndex:
    vectors = embed_documents([chunk["text"] for chunk in chunks])
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return DocumentIndex(index, chunks)


def _save_index(document_id: str, document_index: DocumentIndex) -> None:
    destination = VECTORSTORE_DIR / document_id
    destination.mkdir(exist_ok=True)
    faiss.write_index(document_index.index, str(destination / "index.faiss"))
    (destination / "chunks.json").write_text(json.dumps(document_index.chunks, ensure_ascii=False), encoding="utf-8")


def index_uploaded_pdf(file_name: str, pdf_bytes: bytes) -> tuple[DocumentIndex, dict]:
    ensure_directories()
    pages = extract_pages(pdf_bytes)
    chunks = split_pages(pages)
    if not chunks:
        raise ValueError("No se encontraron fragmentos de texto para indexar.")
    document_index = build_index(chunks)
    document_id = hashlib.sha256(pdf_bytes).hexdigest()[:16]
    _save_index(document_id, document_index)
    return document_index, {"file_name": file_name, "pages": len(pages), "chunks": len(chunks)}
