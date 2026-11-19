# LifeOS AI 🚀
### Your Personal AI Chief of Staff — Powered by Lemma SDK

![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)
![Docker](https://img.shields.io/badge/docker-supported-informational.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)

---

## 📖 Overview
**LifeOS AI** is an advanced AI-powered personal productivity and operations platform ("Your Personal AI Chief of Staff"). Built on top of **FastAPI** and the **Lemma SDK**, it coordinates intelligent agents to manage workflows, automate tasks, and organize life operations through a high-performance backend and a sleek Vite/TypeScript frontend.

---

## 🏗️ Architecture & Tech Stack

- **Backend:** Python 3.11, FastAPI, Uvicorn, SQLAlchemy, structured logging, Lemma SDK integration.
- **Frontend:** TypeScript, Vite, modern HTML5/CSS3 interface components.
- **Containerization & Deployment:** Docker multi-stage builds orchestrated via Docker Compose, serving static frontend assets directly through FastAPI with integrated health checks.

---

## ⚙️ Prerequisites
Ensure you have the following installed on your machine:
- **Docker** & **Docker Compose** (Recommended for easiest setup)
- **Python 3.11+** (If running backend natively)
- **Node.js 20+ & npm** (If running frontend natively)

---

## 🔑 Environment Configuration
Create a `.env` file at the root and a `backend/.env` file based on your deployment needs. **Never commit these files to version control.**

| Variable Name | Description | Default / Example |
| :--- | :--- | :--- |
| `LEMM_ENABLED` | Toggle Lemma SDK integration | `true` |
| `LEMMA_SERVER_URL` | Endpoint for Lemma SDK server | `http://localhost:5000` |
| `UPLOAD_DIR` | Directory for file attachments | `./workspace/uploads` |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./workspace/lifeos.db` |

---

## 🚀 Quick Start Guide

### Path A: Docker Compose (Recommended)
1. Clone the repository and navigate to the root.
2. Create your `.env` files as described above.
3. Run the following command:
   ```bash
   docker compose up --build
   ```
4. Access the application at `http://localhost:8000`.

### Path B: Manual Local Development
**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
npm install
npm run dev
```

---

## 🌐 API Documentation & Navigation
Once the backend is running, you can access the following:
- **Swagger UI:** `http://localhost:8000/api/docs`
- **ReDoc:** `http://localhost:8000/api/redoc`
- **Health Check:** `http://localhost:8000/health`
- **Frontend UI:** `http://localhost:5173` (or via FastAPI static route)

---

## 🛠️ Maintenance & Troubleshooting

- **Port Conflicts:** If `8000` or `5173` are in use, modify the `ports` mapping in `docker-compose.yml` or your local environment variables.
- **Volume Permissions:** If you encounter permission errors with the `./workspace` directory on Linux/macOS, ensure the directory exists and is writable by the user running the Docker daemon: `mkdir -p workspace && chmod 777 workspace`.
- **Missing Variables:** Ensure all required keys in `backend/.env` are populated; the application will fail to initialize if critical configuration is missing.
- **CORS:** For production, ensure `allow_origins` in your FastAPI middleware is restricted to your specific domain rather than using `*`.

---

## 🛡️ Security Note
This project uses Pydantic for strict input validation. Always ensure that your production environment uses strong, unique secrets for any authentication tokens and that your database is backed up regularly.