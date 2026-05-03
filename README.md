 ### DiabetesInsight-RAG 🩺

A Retrieval-Augmented Generation (RAG) system for querying medical information about Type 2 Diabetes, built with LangChain, FAISS, and Ollama.

## 🎯 Overview

DiabetesInsight-RAG is an AI-powered medical assistant that answers questions about Type 2 Diabetes **exclusively based on official medical documents** (WHO, ADA, IMSS, PRONAM). It uses RAG architecture to prevent hallucinations and ensure responses are grounded in verified clinical sources.

## 🏗️ Architecture
PDFs → PyPDFLoader → RecursiveCharacterTextSplitter → HuggingFace Embeddings → FAISS VectorStore
↓
User Query → Embed Query → Similarity Search → Retrieved Chunks → Llama 3.2 → Response

## 📁 Project Structure
DiabetesInsight-RAG/
├── data/
│   └── raw/              # Place your PDF documents here
├── src/
│   ├── ingest.py         # PDF loading, chunking and vector store creation
│   └── app.py            # Streamlit frontend and RAG chain
├── .env                  # API keys (not included in repo)
├── .gitignore
├── requirements.txt
└── README.md

## ⚙️ Tech Stack

| Component | Technology |
|---|---|
| Framework | LangChain 1.2 |
| LLM | Llama 3.2 via Ollama (local) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Store | FAISS |
| Frontend | Streamlit |

## 🔍 How It Works

1. **Ingestion** — PDFs are loaded with `PyPDFLoader` and split into 1000-character chunks with 200-character overlap using `RecursiveCharacterTextSplitter`
2. **Embedding** — Each chunk is converted to a 384-dimensional vector using `all-MiniLM-L6-v2`
3. **Storage** — Vectors are persisted locally using FAISS
4. **Query** — User question is embedded with the same model and top-4 most similar chunks are retrieved
5. **Generation** — Retrieved chunks + question are passed to Llama 3.2 with a strict medical safety prompt
6. **Citation** — Every response displays the source PDF and page number

## 📄 Document Sources

- **WHO** — Global Report on Diabetes
- **ADA** — Standards of Medical Care in Diabetes 2024
- **IMSS** — Guía de Práctica Clínica: Diabetes Mellitus Tipo 2
- **PRONAM** — Programa Nacional de Salud: Diabetes Tipo 2

## 🔒 Safety Design

This system implements a strict medical safety prompt that:
- Restricts responses to information present in the source documents
- Refuses to answer questions outside the scope of Type 2 Diabetes
- Always recommends consulting a medical professional
- Displays source citations with every response

## 🚀 Setup

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed

### Installation

```bash
# Clone the repository
git clone https://github.com/GaneshaDS/DiabetesInsight-RAG.git
cd DiabetesInsight-RAG

# Create virtual environment
python -m venv venv
venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt

# Pull the LLM
ollama pull llama3.2
```

### Add your documents
Place your PDF files in `data/raw/`.

### Run ingestion
```bash
python src/ingest.py
```

### Launch the app
```bash
streamlit run src/app.py
```

## ⚠️ Disclaimer

This system is for informational purposes only. It does not replace professional medical consultation. Always consult a licensed healthcare professional for medical advice.

## 👨‍💻 Author

**Heriberto Ganesha Cortés Valdez**  
Computer Science Engineering Student — Instituto Tecnológico de Morelia  
[GitHub](https://github.com/GaneshaDS) · [LinkedIn](#).



