# DocuMind AI

Agente RAG para consultar el contenido de documentos PDF mediante una interfaz en Streamlit. El sistema extrae el texto por página, lo divide en fragmentos, crea embeddings con Cohere y realiza la búsqueda semántica con FAISS antes de generar cada respuesta.

## Características

- Carga y procesamiento de PDFs con trazabilidad por página.
- Búsqueda semántica local mediante FAISS.
- Respuestas de Gemini limitadas explícitamente al contexto recuperado.
- Fuentes y fragmentos utilizados en cada respuesta.
- Historial conversacional durante la sesión.
- Selector de modelo y cantidad de fragmentos recuperados.
- Índices locales guardados en `vectorstore/` (ignorados por Git).

## Arquitectura

```text
PDF → PyPDF → fragmentos con página → Cohere Embeddings → FAISS
                                                     ↓
Pregunta → Cohere Embeddings → recuperación de fragmentos → Cohere → respuesta + fuentes
```

## Requisitos

- Python 3.11 o superior.
- Una clave de la [API de Cohere](https://dashboard.cohere.com/api-keys).

## Instalación

```bash
git clone <TU_REPOSITORIO>
cd DocuMind-AI
python -m venv .venv
```

Activa el entorno virtual y después instala las dependencias:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copia `.env.example` como `.env` y configura tu clave:

```env
COHERE_API_KEY=tu_clave_real
```

Inicia la aplicación:

```bash
streamlit run app.py
```

## Uso

1. Carga un PDF con texto seleccionable.
2. Espera a que se creen los fragmentos y el índice.
3. Formula preguntas concretas sobre el contenido.
4. Abre **Ver fuentes utilizadas** para comprobar de qué páginas se obtuvo la respuesta.

> Los PDFs escaneados sin capa de texto no se procesan en esta versión. Se puede añadir OCR como mejora futura.

## Despliegue en Oracle Cloud (OCI)

En una instancia Ubuntu:

```bash
sudo apt update && sudo apt install -y python3-venv git
git clone <TU_REPOSITORIO> && cd DocuMind-AI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo 'GEMINI_API_KEY=tu_clave' > .env
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Abre el puerto 8501 en las reglas de ingreso de la VCN y, para producción, ejecuta Streamlit bajo `systemd` detrás de Nginx.

## Privacidad

Los índices FAISS se guardan localmente. Durante el procesamiento, los textos de los fragmentos se envían a Cohere para producir embeddings; al responder, solo se envían los fragmentos recuperados y la pregunta. No subas documentos si no tienes autorización para procesarlos con ese proveedor.

## Estructura

```text
app.py                 # interfaz Streamlit
src/pdf_loader.py      # extracción de texto por página
src/chunker.py         # fragmentación con solapamiento
src/embeddings.py      # embeddings de Gemini
src/rag.py             # índice y búsqueda FAISS
src/chatbot.py         # respuesta fundamentada
```
