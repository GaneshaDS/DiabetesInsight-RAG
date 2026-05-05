"""
Streamlit app for Diabetes Type 2 RAG system.
"""
import os
import re
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
load_dotenv()

VECTORSTORE_PATH = Path(__file__).parent.parent / "vectorstore"

def clean_question(q: str) -> str:
    """Normaliza y limpia la pregunta del usuario."""
    q = re.sub(r'\s+', ' ', q).strip()
    return q


MEDICAL_PROMPT = PromptTemplate(
    template="""Eres un asistente médico especializado en diabetes tipo 2.

Contexto médico proporcionado:
{context}

Instrucciones:
- Prioriza SIEMPRE la información del contexto para recomendaciones específicas.
- Si el contexto no contiene una definición básica (como qué es la enfermedad), puedes usar tu conocimiento general para dar una respuesta introductoria breve, pero siempre aclara qué partes vienen de los documentos oficiales.
- Mantén un tono profesional y basado en evidencia.

Pregunta: {question}
Respuesta:""",
    input_variables=["context", "question"]
)


@st.cache_resource
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        encode_kwargs={"normalize_embeddings": True}
    )
    # Resolvemos la ruta a absoluta para evitar problemas con FAISS en Windows
    load_path = str(VECTORSTORE_PATH.resolve())
    return FAISS.load_local(
        load_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

@st.cache_resource
def load_chain():
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY")
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | MEDICAL_PROMPT
        | llm
        | StrOutputParser()
    )

    return chain, retriever


def main():
    st.set_page_config(
        page_title="Diabetes T2 — Asistente RAG",
        page_icon="🩺",
        layout="wide"
    )

    st.title("🩺 Asistente RAG — Diabetes Tipo 2")
    st.caption("Respuestas basadas exclusivamente en documentos médicos oficiales (OMS, ADA, IMSS, PRONAM)")

    if not VECTORSTORE_PATH.exists():
        st.error("Vectorstore no encontrado. Corre `python src/ingest.py` primero.")
        return

    try:
        chain, retriever = load_chain()
    except Exception as e:
        st.error(f"Error cargando el modelo: {e}")
        return

    question = st.chat_input("Escribe tu pregunta sobre diabetes tipo 2...")

    if question:
        question = clean_question(question)
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Buscando en documentos médicos..."):
                try:
                    answer = chain.invoke(question)
                    source_docs = retriever.invoke(question)

                    st.write(answer)

                    if source_docs:
                        with st.expander("📄 Fuentes consultadas"):
                            seen = set()
                            for doc in source_docs:
                                fname = doc.metadata.get("source_file", "Documento desconocido")
                                page = doc.metadata.get("page", "?")
                                key = f"{fname}_p{page}"
                                if key not in seen:
                                    st.markdown(f"- **{fname}** — página {page}")
                                    seen.add(key)

                except Exception as e:
                    st.error(f"Error generando respuesta: {e}")

    with st.sidebar:
        st.markdown("### 🩺 Diabetes RAG")
        st.markdown("Sistema de recuperación de información médica basado en documentos oficiales.")
        st.divider()
        st.markdown("**Documentos base:**")
        st.markdown("- OMS — Global Report on Diabetes\n- ADA Standards of Care 2024\n- Guía IMSS DM2\n- PRONAM México")
        st.divider()
        st.warning("⚠️ Este sistema es informativo. No reemplaza la consulta médica profesional.")


if __name__ == "__main__":
    main()