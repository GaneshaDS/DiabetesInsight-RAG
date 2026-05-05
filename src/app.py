"""
Streamlit app for Diabetes Type 2 RAG system.
- Conversation memory via st.session_state (sliding-window history)
- Two-chain architecture: contextualize question → RAG response
- Tech-Minimalist / Dark Academia UI
"""
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from styles import CUSTOM_CSS

load_dotenv()


def get_secret(key: str) -> str | None:
    """Lee un secreto desde st.secrets (Streamlit Cloud) o desde .env (local).
    Prioriza st.secrets para garantizar seguridad en producción."""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key)

VECTORSTORE_PATH = Path(__file__).parent.parent / "vectorstore"

# Número de turnos (pares user/assistant) en la ventana deslizante del prompt
MAX_HISTORY_TURNS = 3

# Avatares personalizados
AVATAR_USER      = "👤"
AVATAR_ASSISTANT = "🩺"

# Preguntas sugeridas para el estado vacío
SUGGESTED_QUESTIONS = [
    "¿Qué es la diabetes tipo 2?",
    "¿Cuáles son los criterios de diagnóstico?",
    "¿Cuál es el tratamiento inicial si HbA1c > 8%?",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_question(q: str) -> str:
    """Normaliza y limpia la pregunta del usuario."""
    return re.sub(r'\s+', ' ', q).strip()


def format_history(messages: list, max_turns: int) -> str:
    """Formatea los últimos N turnos como texto compacto para el prompt."""
    pairs: list[tuple[str, str]] = []
    i = 0
    while i < len(messages) - 1:
        if messages[i]["role"] == "user" and messages[i + 1]["role"] == "assistant":
            pairs.append((messages[i]["content"], messages[i + 1]["content"]))
            i += 2
        else:
            i += 1
    recent = pairs[-max_turns:]
    lines = []
    for u, a in recent:
        lines.append(f"Usuario: {u}")
        lines.append(f"Asistente: {a}")
    return "\n".join(lines) if lines else "Sin historial previo."


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

CONTEXTUALIZE_PROMPT = PromptTemplate(
    template="""Dado el siguiente historial de conversación y una nueva pregunta del usuario,
reformula la pregunta como una pregunta autocontenida que pueda entenderse sin el historial.
Si la pregunta ya es autocontenida, devuélvela sin cambios.
Devuelve SOLO la pregunta reformulada, sin explicaciones adicionales.

Historial:
{chat_history}

Pregunta actual: {question}
Pregunta reformulada:""",
    input_variables=["chat_history", "question"]
)

MEDICAL_PROMPT = PromptTemplate(
    template="""Eres un asistente médico especializado en diabetes tipo 2.

Historial reciente de la conversación:
{chat_history}

Contexto médico proporcionado:
{context}

Instrucciones:
- Prioriza SIEMPRE la información del contexto para recomendaciones específicas.
- Si el contexto no contiene una definición básica (como qué es la enfermedad), puedes usar tu conocimiento general para dar una respuesta introductoria breve, pero siempre aclara qué partes vienen de los documentos oficiales.
- Mantén coherencia con el historial si la pregunta hace referencia a algo anterior.
- Mantén un tono profesional y basado en evidencia.

Pregunta: {question}
Respuesta:""",
    input_variables=["chat_history", "context", "question"]
)


# ---------------------------------------------------------------------------
# Recursos cacheados (sin estado — seguros para @st.cache_resource)
# ---------------------------------------------------------------------------

@st.cache_resource
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        encode_kwargs={"normalize_embeddings": True}
    )
    load_path = str(VECTORSTORE_PATH.resolve())
    return FAISS.load_local(
        load_path,
        embeddings,
        allow_dangerous_deserialization=True
    )


@st.cache_resource
def load_retriever_and_llm():
    """Carga y cachea el retriever y el LLM.
    La chain se construye en main() para inyectar el historial dinámicamente."""
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        api_key=get_secret("GROQ_API_KEY")
    )
    return retriever, llm


# ---------------------------------------------------------------------------
# Lógica de respuesta (reutilizable desde input y botones sugeridos)
# ---------------------------------------------------------------------------

def run_rag(question: str, retriever, llm) -> None:
    """Ejecuta el pipeline RAG completo para una pregunta y actualiza session_state."""
    question = clean_question(question)

    with st.chat_message("user", avatar=AVATAR_USER):
        st.write(question)

    st.session_state.messages.append({"role": "user", "content": question})

    history_text = format_history(st.session_state.messages[:-1], MAX_HISTORY_TURNS)

    with st.chat_message("assistant", avatar=AVATAR_ASSISTANT):
        with st.spinner("Buscando en documentos médicos..."):
            try:
                # Paso 1: Contextualizar pregunta con el historial
                contextualize_chain = CONTEXTUALIZE_PROMPT | llm | StrOutputParser()
                standalone_question = contextualize_chain.invoke({
                    "chat_history": history_text,
                    "question": question
                })

                # Paso 2: Recuperar documentos relevantes
                source_docs = retriever.invoke(standalone_question)
                context_text = "\n\n".join(doc.page_content for doc in source_docs)

                # Paso 3: Generar respuesta
                rag_chain = MEDICAL_PROMPT | llm | StrOutputParser()
                answer = rag_chain.invoke({
                    "chat_history": history_text,
                    "context": context_text,
                    "question": standalone_question
                })

                st.write(answer)

                # Fuentes consultadas
                if source_docs:
                    with st.expander("📄 Fuentes consultadas"):
                        seen: set[str] = set()
                        for doc in source_docs:
                            fname = doc.metadata.get("source_file", "Documento desconocido")
                            page  = doc.metadata.get("page", "?")
                            key   = f"{fname}_p{page}"
                            if key not in seen:
                                st.markdown(f"- **{fname}** — página {page}")
                                seen.add(key)

                st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                st.error(f"Error generando respuesta: {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(
        page_title="DiabetesInsight — Asistente RAG",
        page_icon="🩺",
        layout="wide"
    )

    # ── Inyección de CSS personalizado ──────────────────────────────────────
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # ── Vectorstore: verificar o construir automáticamente ──────────────────
    if not VECTORSTORE_PATH.exists():
        # En Streamlit Cloud el vectorstore no existe en el repo; lo construimos.
        # Los PDFs deben estar en data/raw/ (incluidos en el repo o descargados).
        DATA_PATH = Path(__file__).parent.parent / "data" / "raw"
        if not DATA_PATH.exists() or not list(DATA_PATH.glob("*.pdf")):
            st.error(
                "⚠️ Vectorstore y PDFs fuente no encontrados.  \n"
                "Incluye los PDFs en `data/raw/` en tu repositorio o "
                "ejecuta `python src/ingest.py` localmente y sube la carpeta `vectorstore/`."
            )
            return

        with st.spinner("⚙️ Construyendo base de conocimiento por primera vez (esto solo ocurre una vez)..."):
            try:
                # Importa ingest en tiempo de ejecución para no cargar siempre
                ingest_path = str(Path(__file__).parent)
                if ingest_path not in sys.path:
                    sys.path.insert(0, ingest_path)
                from ingest import load_documents, split_documents, create_vectorstore
                docs   = load_documents()
                chunks = split_documents(docs)
                create_vectorstore(chunks)
                st.success("✅ Base de conocimiento construida. Recargando...")
                st.rerun()
            except Exception as e:
                st.error(f"Error construyendo el vectorstore: {e}")
                return

    # ── Carga de recursos ───────────────────────────────────────────────────
    try:
        retriever, llm = load_retriever_and_llm()
    except Exception as e:
        st.error(f"Error cargando el modelo: {e}")
        return

    # ── Inicialización de session_state ─────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None

    # ── Sidebar ─────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🩺 DiabetesInsight")
        st.caption("Asistente RAG especializado en diabetes tipo 2.")
        st.divider()
        st.markdown("**Documentos base:**")
        st.markdown(
            "- OMS — Global Report on Diabetes\n"
            "- ADA Standards of Care 2024\n"
            "- Guía IMSS DM2\n"
            "- PRONAM México"
        )
        st.divider()

        if st.button("🗑️ Nueva conversación", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pending_question = None
            st.rerun()

        st.divider()
        st.warning("⚠️ Sistema informativo. No reemplaza la consulta médica profesional.")

    # ── Encabezado ──────────────────────────────────────────────────────────
    st.markdown("## 🩺 DiabetesInsight")
    st.caption("Respuestas fundamentadas en documentos médicos oficiales · OMS · ADA · IMSS · PRONAM")

    # ── Empty state: preguntas sugeridas ─────────────────────────────────────
    if not st.session_state.messages:
        st.markdown(
            "<p style='color:#888899; font-size:0.9rem; margin: 2rem 0 0.75rem;'>"
            "Preguntas frecuentes para comenzar:</p>",
            unsafe_allow_html=True
        )
        cols = st.columns(len(SUGGESTED_QUESTIONS))
        for col, q in zip(cols, SUGGESTED_QUESTIONS):
            with col:
                st.markdown('<div class="suggested-btn">', unsafe_allow_html=True)
                if st.button(q, key=f"sug_{q}"):
                    st.session_state.pending_question = q
                st.markdown('</div>', unsafe_allow_html=True)

    # ── Renderizado del historial previo ─────────────────────────────────────
    for msg in st.session_state.messages:
        avatar = AVATAR_USER if msg["role"] == "user" else AVATAR_ASSISTANT
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

    # ── Despachar pregunta sugerida (si la hay) ──────────────────────────────
    if st.session_state.pending_question:
        q = st.session_state.pending_question
        st.session_state.pending_question = None
        run_rag(q, retriever, llm)
        st.rerun()

    # ── Input de nueva pregunta ──────────────────────────────────────────────
    question = st.chat_input("Escribe tu pregunta sobre diabetes tipo 2...")
    if question:
        run_rag(question, retriever, llm)


if __name__ == "__main__":
    main()