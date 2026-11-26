# SAKHI — Voice-First Household Prioritization & ASHA Workflow Assistant

SAKHI is a local-first web application built with **FastAPI**, **SQLite**, and **HTML/CSS/Vanilla JavaScript** to help ASHA healthcare workers prioritize households, plan and document field visits, track follow-ups, and use multilingual voice automation powered by **Sarvam AI**.

---

## Project Structure

```text
Sakhi_v1.0/
├── backend/
│   ├── asha_data.db              # SQLite database (households, pregnancies, children, visits, workers)
│   ├── backend.py                # Core SQLite & clinical flag/metrics logic
│   └── vacs.json                 # Vaccination schedule reference
├── frontend/
│   ├── index.html                # Single-page application UI (Desktop & Mobile views)
│   ├── app.js                    # Application controller, i18n (EN/HI/KN), voice & form automation
│   └── style.css                 # Responsive styling
├── src/
│   ├── api_link.py               # FastAPI server, REST API routes & static frontend serving
│   ├── prioritization.py         # Deterministic rule-based household prioritization engine
│   ├── sarvam_service.py         # Sarvam AI STT (saaras:v4), TTS (bulbul:v3), Translate (mayura:v1), Chat (sarvam-105b)
│   ├── multilingual_nlp.py       # Kannada / Hindi / English script detection & Indic field extraction
│   ├── voice_form_extractor.py   # Schema-aware voice-to-form field mapping
│   ├── voice_service.py          # Transcript parsing, date resolution & danger-sign detection
│   ├── voice_action_service.py   # Action previews & confirmation-gated database updates
│   └── chatbot_service.py        # Page-aware contextual AI assistant grounded in SQLite & NHM KB
├── .env                          # Local environment variables (keep private)
├── .env.example                  # Environment template
├── run.py                        # Optional startup helper
├── test_integration.py           # End-to-end integration test suite
└── README.md
```

---

## Setup & Running Locally

### 1. Configure Environment Variables
Copy `.env.example` to `.env` (if not already created) and set your Sarvam AI subscription key:

```env
SARVAM_API_KEY=your_sarvam_api_key_here
SARVAM_STT_MODEL=saaras:v4
SARVAM_TTS_MODEL=bulbul:v3
```

### 2. Start the Server
From the project root:

```powershell
uvicorn src.api_link:app --host 127.0.0.1 --port 8000
```

Open **`http://127.0.0.1:8000`** in your browser.

### 3. Demo Login
- **Phone Number:** `9876543210`
- **Password:** `pass12`

---

## Key Capabilities

- **Household Priority Summary & Visits Queue**: Rule-based ranking (`RED` Immediate Escalation, `ORANGE` High Priority, `YELLOW` Overdue/Due Today, `GREEN` Routine) with plain-language explanations and missing-data verification warnings.
- **Multilingual UI**: Instant switching between **English**, **हिन्दी (Hindi)**, and **ಕನ್ನಡ (Kannada)** from the top toolbar.
- **Voice-First Form Filling**: Inside **Maternal Health** or **Vaccine Tracker** registration forms, tap **Voice** to dictate details in Kannada, Hindi, or English, merge across multiple recordings, edit, and save to SQLite.
- **Page-Aware AI Assistant**: On **Home**, **Alerts**, and **AI Chatbot**, ask natural questions about pending tasks, alerts, or selected beneficiaries, with optional explicit **Share Current Tab** context and **Sarvam TTS** audio playback.

---

## Verification

Run the end-to-end integration test suite from the project root:

```powershell
python test_integration.py
```
