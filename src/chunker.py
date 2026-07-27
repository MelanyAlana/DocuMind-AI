from __future__ import annotations


def split_pages(pages: list[dict], chunk_size: int = 1200, overlap: int = 180) -> list[dict]:
    """Divide cada página en ventanas solapadas para conservar el contexto."""
    chunks = []
    for item in pages:
        text = item["text"]
        start = 0
        while start < len(text):
            end = min(len(text), start + chunk_size)
            if end < len(text):
                boundary = text.rfind(" ", start + chunk_size - 200, end)
                if boundary > start:
                    end = boundary
            content = text[start:end].strip()
            if content:
                chunks.append({"page": item["page"], "text": content})
            if end >= len(text):
                break
            start = max(end - overlap, start + 1)
    return chunks
