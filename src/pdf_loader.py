from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader


def extract_pages(pdf_bytes: bytes) -> list[dict]:
    """Extrae texto por página, preservando el número de página original."""
    reader = PdfReader(BytesIO(pdf_bytes))
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append({"page": number, "text": text})
    if not pages:
        raise ValueError("El PDF no contiene texto seleccionable. Prueba con un PDF que no sea escaneado.")
    return pages
