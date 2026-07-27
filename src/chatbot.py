from __future__ import annotations

import cohere

from .config import get_api_key
from .rag import DocumentIndex

SYSTEM_INSTRUCTION = """Eres DocuMind AI. Responde siempre en español y ÚNICAMENTE con la información del CONTEXTO proporcionado. Si el contexto no contiene la respuesta, dilo claramente. No inventes datos ni uses conocimiento externo. Sé conciso y, cuando sea útil, indica que la afirmación procede de una página concreta."""


def answer_question(index: DocumentIndex, question: str, top_k: int, model: str) -> dict:
    sources = index.search(question, top_k)
    context = "\n\n".join(f"[Página {item['page']}]\n{item['text']}" for item in sources)
    prompt = f"CONTEXTO:\n{context}\n\nPREGUNTA: {question}"
    client = cohere.ClientV2(api_key=get_api_key())
    response = client.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    answer = "".join(part.text for part in response.message.content if getattr(part, "type", "") == "text").strip()
    answer = answer or "No fue posible generar una respuesta."
    return {"answer": answer, "sources": [{"page": item["page"], "text": item["text"][:500] + ("…" if len(item["text"]) > 500 else "")} for item in sources]}
