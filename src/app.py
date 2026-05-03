"""
Streamlit app for Diabetes Type 2 RAG system.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM
load_dotenv()

VECTORSTORE_PATH = Path("C:/vectorstore_diabetes")


MEDICAL_PROMPT = PromptTemplate(
    template="""Eres un asistente médico especializado en diabetes tipo 2.
Usa los siguientes fragmentos de documentos médicos para responder la pregunta.

Contexto:
{context}

Instrucciones:
- Responde usando la información del contexto anterior.
- Si el contexto contiene información relevante, úsala para dar una respuesta clara.
- Si la pregunta es sobre un tema completamente diferente a la diabetes, responde: "Esta pregunta está fuera del alcance de este sistema. Te recomiendo consultar a un médico."
- No inventes datos que no estén en el contexto.

Pregunta: {question}

Respuesta:""",
    input_variables=["context", "question"]
)


@st.cache_resource
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        encode_kwargs={"normalize_embeddings": True}
    )
    return FAISS.load_local(
        str(VECTORSTORE_PATH),
        embeddings,
        allow_dangerous_deserialization=True
    )

@st.cache_resource
def load_chain():
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    llm = OllamaLLM(
        model="llama3.2",
        temperature=0.3,
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