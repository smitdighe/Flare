# Flare

Multi-agent security alert triage engine. Classifies, enriches, and reasons over IDS alerts in real time using a LangGraph pipeline backed by Groq, AbuseIPDB, VirusTotal, and Gemini with MITRE ATT&CK RAG grounding.

![Pipeline](https://img.shields.io/badge/pipeline-classify→enrich→reason-ff9500) ![Python](https://img.shields.io/badge/python-3.11+-3776ab) ![React](https://img.shields.io/badge/react-19-61dafb)

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Frontend (React)                    │
│  Vite + Tailwind + Three.js + Motion                 │
│  SSE live feed · Command palette · Threat topology   │
└──────────────────────┬───────────────────────────────┘
                       │ EventSource + REST
┌──────────────────────▼───────────────────────────────┐
│                  Backend (FastAPI)                     │
│                                                       │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│   │ CLASSIFY │──▶│  ENRICH  │──▶│  REASON  │──▶ END │
│   │  Groq    │   │ AbuseIPDB│   │ Gemini   │        │
│   │ Llama 3.1│   │ VirusTotal│  │ + RAG    │        │
│   └──────────┘   └──────────┘   └──────────┘        │
│        │              │               │               │
│        ▼              ▼               ▼               │
│   Severity +      IOC rep +     MITRE technique +    │
│   attack type     VT verdict    remediation steps    │
└──────────────────────────────────────────────────────┘
```

## Features

- **Real-time SSE stream** -- alerts flow in via Server-Sent Events with configurable speed (fast/balanced/thorough)
- **Three-stage pipeline** -- classify (Groq/Llama), enrich (AbuseIPDB + VirusTotal), reason (Gemini + MITRE RAG)
- **Live dashboard** -- alert feed, threat clusters, signal topology, health metrics, evaluation panel
- **Command palette** -- `Ctrl+K` / `Cmd+K` for quick navigation and actions
- **Keyboard navigation** -- `j`/`k` to move, `Enter` to inspect, `Escape` to dismiss
- **Pause/resume** -- control the live stream without losing existing alerts
- **Eval harness** -- 24 labeled ground-truth alerts with confusion matrix and F1 scoring
- **Provider benchmark** -- compare Groq (fast) vs Gemini (quality) on the same alert side by side

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- API keys for Groq, Gemini, AbuseIPDB, VirusTotal

### 1. Clone

```bash
git clone https://github.com/<you>/flare.git
cd flare
```

### 2. Configure

```bash
cd backend
cp .env.example .env
```

Fill in your API keys in `.env`:

```
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=...
ABUSEIPDB_API_KEY=...
VIRUSTOTAL_API_KEY=...
```

### 3. Run

**Windows:** Double-click `start.bat`

**Manual:**

```bash
# Terminal 1 -- Backend
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 -- Frontend
cd frontend
npm install
npm run dev
```

Open **http://localhost:5174**

## Project Structure

```
flare/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + endpoints
│   │   ├── config.py            # Pipeline speed/toggle config
│   │   ├── models.py            # Pydantic models
│   │   ├── store.py             # Thread-safe in-memory alert store
│   │   ├── health.py            # API key health checker (60s cache)
│   │   ├── stream.py            # SSE stream manager (pause/resume)
│   │   ├── eval.py              # Eval harness with confusion matrix
│   │   ├── data/
│   │   │   ├── sample_alerts.py # Fake alert generator
│   │   │   ├── cicids_loader.py # CICIDS2017 dataset loader
│   │   │   └── generator.py     # Shared alert generator
│   │   ├── pipeline/
│   │   │   ├── graph.py         # LangGraph pipeline definition
│   │   │   ├── classify.py      # Stage 1: Groq/Llama classifier
│   │   │   ├── enrich.py        # Stage 2: AbuseIPDB + VT enrichment
│   │   │   ├── reason.py        # Stage 3: Gemini + MITRE RAG reasoning
│   │   │   ├── benchmark.py     # Groq vs Gemini benchmark
│   │   │   └── virustotal.py    # VirusTotal API client
│   │   └── rag/
│   │       ├── retriever.py     # TF-IDF retriever over MITRE corpus
│   │       └── mitre_corpus.py  # 30 MITRE ATT&CK techniques
│   ├── requirements.txt
│   ├── .env.example
│   └── .env                     # (not committed)
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Root component
│   │   ├── main.jsx             # Entry point + ErrorBoundary
│   │   ├── components/
│   │   │   ├── DashboardView.jsx    # Dashboard shell
│   │   │   ├── CommandBar.jsx       # Top navigation bar
│   │   │   ├── SideRail.jsx         # Left navigation rail
│   │   │   ├── WorkspacePanel.jsx   # Main content area
│   │   │   ├── DashboardHeader.jsx  # Stats header
│   │   │   ├── FilterStrip.jsx      # Severity/type filters
│   │   │   ├── OperationsRail.jsx   # Right sidebar
│   │   │   ├── AlertTable.jsx       # Alert list table
│   │   │   ├── AlertDetailDrawer.jsx # Alert detail slide-out
│   │   │   ├── CommandPalette.jsx   # Ctrl+K command palette
│   │   │   ├── ErrorBoundary.jsx    # React error boundary
│   │   │   ├── FlareLanding.jsx     # Landing page
│   │   │   ├── SignalTopology.jsx   # 2D network graph
│   │   │   ├── ThreeTopology.jsx    # 3D topology (Three.js)
│   │   │   ├── ParticleField.jsx    # Background particle animation
│   │   │   ├── ShaderBackdrop.jsx   # WebGL shader backdrop
│   │   │   ├── PipelineStageInspector.jsx # Pipeline detail modal
│   │   │   ├── TelemetrySparkline.jsx # Mini sparkline chart
│   │   │   ├── AnimatedNumber.jsx   # Animated counter
│   │   │   ├── MetricBlock.jsx      # Metric display block
│   │   │   ├── StatusDot.jsx        # Status indicator dot
│   │   │   └── Icon.jsx             # Material icon wrapper
│   │   ├── hooks/
│   │   │   ├── useMotionPointer.js  # Mouse position tracker
│   │   │   └── useScrollProgress.js # Scroll progress hook
│   │   ├── data/
│   │   │   └── mockAlerts.js        # Mock alert data
│   │   └── styles/
│   │       ├── tokens.css           # Design tokens
│   │       ├── app.css              # Global styles
│   │       ├── landing.css          # Landing page styles
│   │       └── dashboard.css        # Dashboard styles
│   ├── package.json
│   └── vite.config.js
├── start.bat                   # One-click launcher (Windows)
├── .gitignore
└── README.md
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/stream` | SSE alert stream |
| `GET` | `/api/v1/alerts` | List alerts (filter by severity, attack_type, search) |
| `GET` | `/api/v1/alerts/{id}` | Alert detail with full pipeline trace |
| `GET` | `/api/v1/alerts/correlated/list` | Source IP correlation clusters |
| `GET` | `/api/v1/stats` | Dashboard statistics |
| `GET` | `/api/v1/health` | API key health status (60s cached) |
| `GET` | `/api/v1/eval` | Eval harness results |
| `GET` | `/api/v1/benchmark` | Groq vs Gemini benchmark |
| `POST` | `/api/v1/seed` | Seed N alerts into the store |
| `POST` | `/api/v1/stream/pause` | Pause the stream |
| `POST` | `/api/v1/stream/resume` | Resume the stream |
| `POST` | `/api/v1/stream/config` | Update pipeline config (speed, toggles) |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes | -- | Groq API key for classification |
| `GEMINI_API_KEY` | Yes | -- | Google Gemini API key for reasoning |
| `ABUSEIPDB_API_KEY` | No | -- | AbuseIPDB key for IP reputation |
| `VIRUSTOTAL_API_KEY` | No | -- | VirusTotal key for IP/hash lookups |
| `FLARE_DATA_MODE` | No | `hybrid` | `fake`, `cicids`, or `hybrid` |
| `CICIDS_CSV_PATH` | No | -- | Path to CICIDS2017 CSV (hybrid mode) |
| `CORS_ORIGINS` | No | `*` | Comma-separated allowed origins |

## Tech Stack

- **Backend:** Python, FastAPI, Uvicorn, LangGraph, Pydantic
- **LLMs:** Groq (Llama 3.1 8B), Google Gemini 1.5 Flash
- **Enrichment:** AbuseIPDB, VirusTotal
- **RAG:** TF-IDF + cosine similarity over 30 MITRE ATT&CK techniques
- **Frontend:** React 19, Vite 8, Tailwind CSS 4, Three.js, Motion (Framer)

## License

Private project.
