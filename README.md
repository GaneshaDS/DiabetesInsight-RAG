# 🩺 DiabetesInsight-RAG

A professional **Retrieval-Augmented Generation (RAG)** system designed for querying official medical information regarding **Type 2 Diabetes**, optimized for high performance with **Llama 3.3 (Groq)** and deployed in the cloud.

---

## 🌐 Live Demo

🚀 Try the app here:  
👉 https://diabetesinsight-rag-jnv7zjh9qqtgmfat6nr7ke.streamlit.app/

---

## 🎯 Overview

**DiabetesInsight-RAG** is an AI-powered medical assistant that answers questions based exclusively on official medical documents.

Unlike generic LLMs, this system uses a **Retrieval-Augmented Generation (RAG)** architecture to reduce hallucinations and ensure every response is grounded in verified clinical sources such as:

- World Health Organization (WHO)
- American Diabetes Association (ADA)
- Instituto Mexicano del Seguro Social (IMSS)
- PRONAM

---

## 🏗️ Cloud Architecture

The system follows a hybrid RAG pipeline:

### 1. Data Ingestion
- PDF medical documents are loaded and processed
- Text is chunked into semantic fragments
- Chunks are converted into vector embeddings

### 2. Retrieval
- **FAISS** performs similarity search to retrieve the most relevant chunks in milliseconds

### 3. Inference / Generation
- Retrieved context is injected into **Llama 3.3**
- Model inference runs on **Groq Cloud LPUs** for ultra-fast responses

---

## 📁 Project Structure

```bash
DiabetesInsight-RAG/
├── .streamlit/
│   └── config.toml          # UI configuration
├── data/
│   └── raw/                 # Medical PDFs (WHO, ADA, IMSS, etc.)
├── src/
│   ├── ingest.py            # PDF ingestion + vectorization pipeline
│   └── app.py               # Streamlit application
├── vectorstore/             # Persistent FAISS database
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Tech Stack

| Component | Technology |
|---|---|
| Orchestrator | LangChain 0.3 |
| LLM | Llama 3.3 via Groq Cloud |
| Embeddings | all-MiniLM-L6-v2 |
| Vector Database | FAISS |
| Frontend | Streamlit |
| Hosting | Streamlit Cloud |

---

## ✨ Features

### 🔍 Verified Medical QA
Answers are generated only from trusted medical documentation.

### ⚡ Fast Inference
Powered by **Groq LPUs** for near-instant response times.

### 🧠 Session Memory
Maintains conversational context during the current session using:

```python
st.session_state
```

### 🔄 Auto-Ingest Pipeline
On first launch:

- checks if vectorstore exists
- automatically processes PDFs if missing

### 🔐 Secrets Management
Secure API handling with:

- `.env`
- `st.secrets`

### 🎨 Premium UI/UX
Custom interface with:

- Dark minimalist aesthetic
- Custom avatars
- FAQ system

---

## 🚀 Local Installation

### Clone repository

```bash
git clone https://github.com/GaneshaDS/DiabetesInsight-RAG.git
cd DiabetesInsight-RAG
```

### Create virtual environment

```bash
python -m venv venv
```

Activate environment:

**Windows**
```bash
venv\Scripts\activate
```

**Linux / Mac**
```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create:

### `.env`
or

### `.streamlit/secrets.toml`

```toml
GROQ_API_KEY="your_api_key_here"
HUGGINGFACEHUB_API_TOKEN="your_token_here"
```

---

## ▶️ Run App

```bash
streamlit run src/app.py
```

---

## ⚠️ Medical Disclaimer

> This project is intended for **academic and informational purposes only**.  
> It is **not** a substitute for professional medical advice, diagnosis, or treatment.

Always consult a licensed healthcare professional.

---

## 👨‍💻 Author

**Heriberto Ganesha Cortés Valdez**  
Computer Systems Engineering Student  
Instituto Tecnológico de Morelia  

**Focus Areas**
- Artificial Intelligence
- RAG Systems
- Cloud Computing
- Applied Machine Learning

---

## 🌟 Future Improvements

- [ ] Docker containerization
- [ ] Multi-document source attribution
- [ ] Citation highlighting
- [ ] User authentication
- [ ] Deployment on AWS/GCP
- [ ] Observability & analytics dashboard

---

## 📜 License

MIT License
