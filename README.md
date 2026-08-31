# 🚀 LifeOS AI — Your Personal AI Chief of Staff

> Powered by **FastAPI**, **Lemma SDK**, **ChromaDB**, and **React + Vite + TypeScript**.

LifeOS AI is an intelligent executive assistant and personal operating system designed to automate task orchestration, document processing, contextual memory retrieval, and life administrative workflows.

---

## 📌 Executive Summary

LifeOS AI bridges personal data streams (documents, tasks, calendars, notes) with agentic AI models. Utilizing Lemma SDK for autonomous agent collaboration and ChromaDB for semantic memory retrieval, LifeOS AI delivers proactive insights and workflow execution via a modern React interface and lightweight REST APIs.

---

## 🏗️ System Architecture

```
                                  +-----------------------+
                                  |   React + Vite SPA    |
                                  | (TypeScript/Lucide UI)|
                                  +-----------+-----------+
                                              |
                                       REST / JSON API
                                              |
                                              v
                                  +-----------+-----------+
                                  |  FastAPI Web Server   |
                                  |   (main.py Gateway)   |
                                  +-----+-----------+-----+
                                        |           |
               +------------------------+           +-----------------------+
               |                                                            |
               v                                                            v
+--------------+---------------+                            +---------------+---------------+
|    Lemma Agentic Engine      |                            |    Storage & Vector Layer     |
| - Task Scheduler Agent       |                            | - SQLite (SQLAlchemy Async)   |
| - Document Intelligence Agent|                            | - ChromaDB Vector Store       |
| - Contextual Memory Agent    |                            | - PyTesseract / PDF Extractors|
+------------------------------+                            +-------------------------------+
```

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (v0.115.5) with `uvicorn`
- **Agent Framework**: Lemma SDK (`lemma-sdk`)
- **Database & ORM**: SQLite (`aiosqlite`), SQLAlchemy 2.0 (Async), Alembic migrations
- **Vector & Embeddings**: ChromaDB, Sentence-Transformers, OpenAI API, Tiktoken
- **Document Processing**: PyPDF2, pdfplumber, Tesseract OCR (`pytesseract`), Pillow, python-docx

### Frontend
- **Framework**: React 18, TypeScript, Vite
- **UI & Animation**: Lucide React icons, Framer Motion, Tailwind/Custom CSS
- **Data & State**: TanStack React Query, Axios, React Router DOM v6
- **Visualizations**: Recharts, React Circular Progressbar, React Big Calendar

---

## 📁 Repository Structure

```
.
├── .env.example           # Example environment variable definitions
├── DEMO_SCRIPT.md         # Walkthrough script for live demonstrations
├── HOW_TO_RUN.md          # Step-by-step launch manual
├── config.py              # Pydantic Settings management
├── database.py            # Async SQLAlchemy database engine & session setup
├── main.py                # FastAPI app initialization & lifecycle hooks
├── models.py              # SQLAlchemy ORM database models
├── dashboard.html         # Interactive visual system dashboard
├── index.html             # Vite SPA HTML entry point
├── package.json           # Frontend dependencies & npm scripts
├── requirements.txt       # Python backend dependencies
├── tsconfig.json          # TypeScript configuration
└── vite.config.ts         # Vite bundler configuration
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.10+
- **Node.js**: 18+ & `npm`
- **Tesseract OCR**: Optional (for scanned document processing)

### 1. Environment Configuration
Copy `.env.example` (or create `.env`) and set your configuration variables:
```bash
cp .env.example .env
```
Ensure required variables are populated with dummy placeholders or real development credentials:
```env
OPENAI_API_KEY=your_openai_api_key_here
LEMMA_ENABLED=true
LEMMA_SERVER_URL=http://localhost:8000
DATABASE_URL=sqlite+aiosqlite:///./lifeos.db
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --port 8000
```
- Interactive API Docs: `http://localhost:8000/api/docs`
- ReDoc Specs: `http://localhost:8000/api/redoc`

### 3. Frontend Setup
```bash
# Install NPM modules
npm install

# Start Vite development server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🔑 Environment Variables Overview

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `OPENAI_API_KEY` | String | *Required* | Key for embeddings and core LLM operations |
| `LEMMA_ENABLED` | Boolean | `true` | Toggle Lemma SDK autonomous agent routines |
| `LEMMA_SERVER_URL` | String | `http://localhost:8000` | Target URL for Lemma agent service endpoint |
| `DATABASE_URL` | String | `sqlite+aiosqlite:///./lifeos.db` | Async SQLAlchemy database connection string |
| `CHROMA_PERSIST_DIRECTORY` | String | `./chroma_db` | Storage path for ChromaDB vector embeddings |
| `LOG_LEVEL` | String | `INFO` | Application logging verbosity (`DEBUG`, `INFO`, `WARN`, `ERROR`) |

---

## ⚡ API Route Reference

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | System health check and database status | No |
| `GET` | `/api/v1/system/metrics` | System telemetry and agent connection state | No |
| `GET` | `/api/v1/tasks` | List all tasks with status filtering | Optional |
| `POST` | `/api/v1/tasks` | Create new autonomous task item | Optional |
| `POST` | `/api/v1/documents/upload` | Ingest multi-modal document (PDF/Docx/Image) | Optional |
| `GET` | `/api/v1/documents` | List uploaded documents and parsing status | Optional |
| `POST` | `/api/v1/agent/query` | Execute query with Lemma Contextual Agent | Optional |
| `POST` | `/api/v1/vector/search` | Query ChromaDB vector index semantically | Optional |

---

## 🗄️ Database Models & Schema Summary

- **`User`**: Account identity, preferences, and API configuration.
- **`Task`**: Autonomous action items containing title, payload, priority, status (`pending`, `in_progress`, `completed`), and scheduling metadata.
- **`Document`**: Raw metadata, MIME type, parsed text content, and reference to ChromaDB collection vectors.
- **`ContextMemory`**: Long-term episodic memory records stored as dense embeddings for multi-turn conversational recall.
- **`AgentLog`**: Diagnostic telemetry tracking Lemma agent runs, latency, execution steps, and sub-agent output logs.

---

## 🤖 Lemma SDK Agent Workflows

LifeOS AI leverages autonomous agent patterns managed through the Lemma SDK (`lemma-sdk`):

1. **Task Scheduler Agent**: Scans pending tasks, evaluates dependencies, predicts priority scores, and dispatches background workflows.
2. **Document Intelligence Agent**: Handles document parsing, OCR extraction via PyTesseract/PDFPlumber, chunks raw text, and generates dense vector embeddings stored in ChromaDB.
3. **Contextual Memory Agent**: Intercepts user queries, fetches top-k relevant embeddings from ChromaDB, compiles system prompts, and synthesizes actionable executive briefings.

---

## 🛠️ Troubleshooting & Commands

For detailed execution workflows and offline verification, consult `HOW_TO_RUN.md` and `DEMO_SCRIPT.md`.

- **Check API Status**:
  ```bash
  curl http://localhost:8000/api/v1/health
  ```
- **Open Interactive Dashboard**:
  Open `dashboard.html` directly in any web browser (`file://.../dashboard.html`). It automatically operates with live backend endpoints or seamlessly transitions to simulated offline mode when offline.