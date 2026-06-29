# 🚀 How to Run LifeOS AI
# Complete step-by-step guide — Windows / Mac / Linux

---

## Prerequisites

Install these first:
- **Python 3.11+** → https://python.org/downloads
- **Node.js 18+** → https://nodejs.org
- **OpenAI API Key** → https://platform.openai.com/api-keys

---

## Step 1 — Get Lemma SDK Running

Lemma SDK is the infrastructure layer. Run it locally:

```bash
# Install Lemma Stack (one command)
curl -fsSL https://raw.githubusercontent.com/lemma-work/lemma-platform/main/install.sh | bash

# Start Lemma (runs at localhost:3711 and localhost:8711)
lemma-stack start

# Install Lemma CLI
uv tool install lemma-terminal

# Login (creates local account)
lemma auth login

# Import LifeOS pod (run from project root)
cd lifeos-ai
lemma pod import ./pod

# Verify it worked
lemma table list   # should show: tasks, goals, documents, expenses, etc.
lemma agent list   # should show: 8 agents
```

**Windows users:** Use WSL2 or Git Bash for the install command.
**Mac users:** May need `brew install uv` first.

---

## Step 2 — Configure Environment

```bash
# In the lifeos-ai/backend directory
cd lifeos-ai/backend
cp ../.env.example .env
```

Open `.env` and set:
```
OPENAI_API_KEY=sk-your-actual-openai-key
LEMMA_SERVER_URL=http://localhost:8711
LEMMA_ENABLED=true
```

---

## Step 3 — Install Backend Dependencies

```bash
cd lifeos-ai/backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Test OCR works (optional — needed for image upload)
# Windows: install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
```

---

## Step 4 — Start the Backend

```bash
# Make sure you're in backend/ with venv active
cd lifeos-ai/backend
source venv/bin/activate   # or venv\Scripts\activate on Windows

# Start the server
python main.py

# You should see:
# ✅ Database initialized
# 🔗 Connecting to Lemma SDK at http://localhost:8711
# ✅ LifeOS AI ready
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

Test it: Open http://localhost:8000 → should show JSON response.
API docs: http://localhost:8000/api/docs

---

## Step 5 — Install Frontend Dependencies

```bash
# In a NEW terminal window
cd lifeos-ai/frontend

# Install packages
npm install
```

---

## Step 6 — Start the Frontend

```bash
cd lifeos-ai/frontend
npm run dev

# You should see:
#   VITE v6.x  ready in Xms
#   ➜  Local:   http://localhost:5173/
```

Open http://localhost:5173 in your browser.

---

## Step 7 — Create Account & Test

1. Open http://localhost:5173
2. Click **Get Started**
3. Register with your name, email, password
4. Land on Dashboard
5. **Upload a bill PDF** → watch 5 agents collaborate
6. **Set a goal** → watch agents build your plan
7. **Chat with AI** → ask about your tasks, bills, goals

---

## Troubleshooting

**Backend won't start:**
```bash
# Check Python version
python --version  # must be 3.11+

# Check if venv is active
which python  # should show path inside venv/

# Install missing packages
pip install -r requirements.txt --upgrade
```

**"Lemma SDK unavailable" warning:**
- This is fine! The app works without Lemma in standalone mode
- Data is stored in SQLite (lifeos.db) instead of Lemma tables
- For full Lemma functionality: run `lemma-stack start`

**Frontend can't reach backend:**
- Make sure backend is running on port 8000
- Check vite.config.ts proxy setting
- Or set: `VITE_API_URL=http://localhost:8000/api` in frontend/.env

**PDF upload fails:**
- Install Tesseract for image OCR
- PDFs work without Tesseract
- Check that ./uploads/ directory is writable

**OpenAI error:**
- Double-check your API key in backend/.env
- Make sure you have credits in your OpenAI account
- GPT-4o is required; GPT-4o-mini works too (change OPENAI_MODEL)

---

## Running in Production

For a production demo or deployment:

```bash
# Backend with gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Frontend build
cd frontend
npm run build
# Serve dist/ with nginx or Vercel

# Or use Railway / Render for one-click deployment
```

---

## Quick Verify Checklist

Before the demo, verify:
- [ ] `http://localhost:8000` returns JSON
- [ ] `http://localhost:8000/api/docs` shows Swagger UI
- [ ] `http://localhost:5173` shows LifeOS landing page
- [ ] Register a new account → lands on Dashboard
- [ ] Upload a sample PDF → returns document summary
- [ ] Create a goal → shows milestones
- [ ] Chat works → AI responds with context
