# 🎬 LifeOS AI — Hackathon Demo Script
# 4-minute demo for Gappy AI Hackathon judges

---

## Opening Line (15 seconds)
> *"Every person in this room manages their life across at least 10 apps.
> Google Calendar, WhatsApp, Notes, Bills, Emails, Tasks — all disconnected.
> LifeOS replaces all of them. One OS. 8 AI agents. Zero cognitive overhead."*

---

## Demo Flow

### Step 1 — Show the Landing Page (20 sec)
- Open http://localhost:5173
- Point to: "8 AI agents collaborating", "4 workflows", "Lemma SDK powered"
- Say: *"Built on Lemma SDK — open-source agent infrastructure. Every agent has a role, scoped data access, and coordinates through workflows."*

---

### Step 2 — Register + Dashboard (30 sec)
- Click "Get Started" → Register with: `demo@lifeos.ai`
- Land on Dashboard
- Say: *"Immediately you see your tasks, goals, upcoming events, unpaid bills. All empty for now — let's fill it up."*

---

### Step 3 — The KILLER DEMO: Upload a Bill (90 sec)
> **This is the WOW moment. Practice this section most.**

- Click "Documents" in sidebar
- Drag and drop `electricity_bill.pdf` (prepare a sample PDF)
- While it processes, explain:
  *"Watch what happens. The Document Agent reads the bill. Then — without any instruction from me — 5 agents are going to collaborate."*
- Result appears. Point to:
  - **Summary:** "Electricity bill from BESCOM, ₹2,400"
  - **Key Dates:** "Due July 5"
  - **Workflow triggered:** bill_processing
  - **Agent steps:** Finance → Planner → Task → Memory → Calendar
- Go to Tasks → Show the auto-created "Pay BESCOM bill" task
- Go to Calendar → Show the reminder event created for July 2
- Go to Expenses → Show the recorded bill
- Say: *"One upload. Five agents. No instructions. This is what agentic software looks like."*

---

### Step 4 — Set a Goal (60 sec)
- Click "Goals"
- Click "Set New Goal"
- Type: *"I want to lose 5 kg in 3 months"*
- Click "Create Goal Plan"
- While loading: *"Goal Agent structures this as SMART goal. Task Agent creates daily checklist. Planner Agent creates workout schedule."*
- Show result:
  - Milestones (Week 1 target, Month 1 target, etc.)
  - First 3 actions
  - Motivational message

---

### Step 5 — AI Chat Demo (45 sec)
- Click "Chat"
- Type: *"What's on my plate today?"*
- Show response — it mentions the bill task, the goal
- Type: *"Summarize my financial situation"*
- Show AI referencing the electricity bill just recorded
- Say: *"The Memory Agent gives every conversation full context. It knows everything."*

---

### Step 6 — Lemma SDK Code Walkthrough (30 sec, optional)
- Show `backend/agents/base_agent.py`:
  ```python
  await lemma.record("tasks", record)       # Lemma table
  await lemma.run_workflow("bill_processing", {...})  # Lemma workflow
  ```
- Show `pod/workflows/bill_processing.yml` — clean YAML workflow definition
- Say: *"Lemma SDK gives us tables, agents, and workflow orchestration in one layer. No need to wire together 5 different services."*

---

## Closing Line (15 sec)
> *"LifeOS isn't another productivity app.
> It's the AI operating system that takes the mental load off entirely.
> Your bills are tracked. Your goals have a plan. Your calendar runs itself.
> That's what LifeOS does."*

---

## Backup Questions (Prepare Answers)

**Q: How is this different from Notion + ChatGPT?**
A: "Notion is a document tool. ChatGPT has no memory or action. LifeOS has persistent memory, agents that act autonomously, and multi-agent workflows that trigger automatically. You don't tell it to do things — it does them."

**Q: How does Lemma SDK add value here?**
A: "Lemma gives us the infrastructure layer — tables with row-level security, agent definitions with scoped access, and workflow graphs that coordinate agents. Without Lemma, I'd need to build all of that myself."

**Q: What would you build next?**
A: "WhatsApp integration via Lemma Surfaces — so you just message your Chief of Staff and it handles everything. That's the real vision: one conversation manages your entire life."

**Q: Does it actually work?**
A: "Yes — every feature you just saw is live. The document processing uses pdfplumber and pytesseract. The agents call GPT-4o. The Lemma tables persist the data. It's not a prototype."

---

## Files to Prepare Before Demo

1. `sample_bill.pdf` — a fake electricity bill PDF with:
   - Amount: ₹2,400
   - Due date: July 5, 2026
   - Vendor: BESCOM

2. Run the app for 30 min before demo — let the backend warm up

3. Clear the database before demo: `rm backend/lifeos.db`

4. Test the full workflow once: upload bill, verify all agents ran

---

## Submission Form (June 30)

**Problem:** People manage life across 10+ disconnected apps, causing missed deadlines, forgotten bills, and constant cognitive overhead.

**Solution:** LifeOS AI — an intelligent operating system that uses 8 AI agents (powered by Lemma SDK infrastructure) to manage tasks, goals, bills, calendar, documents, and memory. Instead of asking questions, it performs work.

**Demo:** [Screen recording of bill upload → 5 agent workflow]

**SDK Usage:** Lemma SDK is the infrastructure backbone — tables, agent definitions, workflow orchestration, and pod configuration all use Lemma primitives.
