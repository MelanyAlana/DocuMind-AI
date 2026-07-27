from __future__ import annotations

import numpy as np
import cohere

from .config import get_api_key

EMBEDDING_MODEL = "embed-v4.0"


def _client() -> cohere.ClientV2:
    return cohere.ClientV2(api_key=get_api_key())


def _embed(texts: list[str], input_type: str) -> np.ndarray:
    response = _client().embed(
        model=EMBEDDING_MODEL,
        inputs=[{"content": [{"type": "text", "text": text}]} for text in texts],
        input_type=input_type,
        embedding_types=["float"],
    )
    matrix = np.asarray(response.embeddings.float_, dtype="float32")
    # El índice usa producto interno como similitud coseno.
    matrix /= np.maximum(np.linalg.norm(matrix, axis=1, keepdims=True), 1e-12)
    return matrix


def embed_documents(texts: list[str]) -> np.ndarray:
    return _embed(texts, "search_document")


def embed_query(text: str) -> np.ndarray:
    return _embed([text], "search_query")[0]
