# 🚀 Autonomous Research Platform (Local-First Multi-Agent System)

A production-grade, local-first multi-agent research platform that autonomously transforms raw user queries into structured, fully sourced professional research reports.

This system is built using **LangGraph** for structured task orchestration and relies entirely on **Ollama** for local LLM inference, ensuring zero external API dependency to guarantee data privacy and reproducibility.

## 🧠 Architecture Overview

The system architecture utilizes a **five-agent cognitive pipeline**:
1. **Planner**: Decomposes the initial user query into actionable sub-tasks and keyword searches.
2. **Scraper**: Performs parallel web and academic data acquisition.
3. **Analyzer**: Filters and synthesizes raw scraped data, generating embeddings using **Nomic** into a local **ChromaDB** vector store.
4. **Writer**: Employs Retrieval-Augmented Generation (RAG) to draft sections following academic formats (IMRAD, literature review structure).
5. **Critic**: Evaluates drafts using self-evaluation loops to detect hallucinations, check cross-document contradictions, and return a conditional routing decision back to the Writer if quality thresholds are unmet.

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.11+**
- **Docker** and **Docker Compose**
- **NVIDIA Container Toolkit** (for GPU acceleration within Docker)
- Local GPU with ~6GB VRAM (optimised for 4-bit GGUF quantization models)

---

## ⚙️ Local Development Setup (Python Virtual Environment)

If you wish to develop or run the application locally without Docker:

1. **Clone the Repository**
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   - **Windows:** `venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Start Ollama Locally (Ensure it's running)**
   Ensure your local instance of Ollama is installed and running. Pull the required models:
   ```bash
   ollama pull llama3.1:8b-instruct-q4_K_M
   ollama pull nomic-embed-text
   ```

6. **Run the Server**
   Start the FastAPI backend server:
   ```bash
   python main.py
   # Or using Uvicorn directly
   uvicorn main:app --host 0.0.0.0 --port 8679
   ```
   The server will be available at: `http://localhost:8679`

---

## 🐳 Production Setup (Docker Compose with GPU)

For a fully packaged, scalable deployment utilizing local GPU acceleration:

1. **Build and Run the Containers**
   The provided `docker-compose.yml` sets up the FastAPI application connected to ChromaDB and a dedicated container for Ollama configured for NVIDIA GPUs.
   ```bash
   docker compose up -d --build
   ```

2. **Download LLM Models inside the Container**
   You need to pull the necessary Llama and Nomic models into the Ollama container volume:
   ```bash
   docker exec -it research_ollama ollama pull llama3.1:8b-instruct-q4_K_M
   docker exec -it research_ollama ollama pull nomic-embed-text
   ```

3. **Access the Service**
   - The API gateway is exposed at: `http://localhost:8679`
   - The local vector store (ChromaDB) persists data via Docker volumes.

---

## 📡 API Endpoints

*(Assuming standard FastAPI routes in `main.py`)*

You can now connect your frontend or test endpoints using tools like Postman, curl, or the built-in Swagger UI:
- **Swagger UI:** `http://localhost:8679/docs`
- **ReDoc:** `http://localhost:8679/redoc`

## 🛡️ Guardrails & Evaluation
The **Critic Node** enforces academic rigor:
- **Source Credibility Scoring**
- **Cross-document Contradiction Detection**
- **Hallucination Auditing**

If the generated draft scores below a `7.0/10.0` or triggers a hallucination flag, the system autonomously routes the execution state back to the Writer node for revision.