# Flare

Multi-agent security alert triage engine. Classifies, enriches, and reasons over IDS alerts in real time using a LangGraph pipeline backed by Groq, AbuseIPDB, VirusTotal, and Gemini with MITRE ATT&CK RAG grounding.

![Pipeline](https://img.shields.io/badge/pipeline-classify→enrich→reason→rules-ff9500) ![Python](https://img.shields.io/badge/python-3.11+-3776ab) ![React](https://img.shields.io/badge/react-19-61dafb) ![Tests](https://img.shields.io/badge/tests-39%20passing-brightgreen)

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Frontend (React)                   │
│  Vite + Tailwind + Three.js + Motion                 │
│  WebSocket live feed · Command palette · 3D topology │
│  Dark/Light theme · Settings · Auth with refresh     │
└──────────────────────┬───────────────────────────────┘
                       │ WebSocket + REST
┌──────────────────────▼───────────────────────────────┐
│                  Backend (FastAPI)                   │
│                                                      │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐         │
│   │ CLASSIFY │──▶│  ENRICH  │──▶│  REASON  │──▶ END│
│   │  Groq    │   │ AbuseIPDB│   │ Gemini   │         │
│   │ Llama 3.1│   │ VirusTotal│  │ + RAG    │         │
│   └──────────┘   └──────────┘   └──────────┘         │
│        │              │               │              │
│        ▼              ▼               ▼              │
│   Severity +      IOC rep +     MITRE technique +    │
│   attack type     VT verdict    remediation steps    │
│                                                      │
│   ┌─────────────────────────────────────────────┐    │
│   │  SQLite + SQLAlchemy + Alembic migrations   │    │
│   │  APScheduler background jobs                │    │
│   │  WebSocket + SSE real-time streams          │    │
│   └─────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

## Features

### Core Pipeline
- **Four-stage pipeline** -- classify (Groq/Llama), enrich (AbuseIPDB + VirusTotal), reason (Gemini + MITRE RAG), rules (custom rule engine with trace)
- **Real-time streaming** -- WebSocket primary, SSE fallback, configurable speed
- **Eval harness** -- 26 labeled ground-truth alerts with confusion matrix, precision/recall/F1, and attack-type breakdown
- **Provider benchmark** -- compare Groq (fast) vs Gemini (quality) on the same alert
- **Health metrics** -- live API key health checker for Groq, Gemini, AbuseIPDB, VirusTotal

### Dashboard
- **Live alert feed** -- real-time alert table with severity indicators
- **3D threat topology** -- Three.js network graph of source IPs
- **Command palette** -- `Ctrl+K` / `Cmd+K` for quick navigation
- **Keyboard navigation** -- `j`/`k` to move, `Enter` to inspect, `Escape` to dismiss
- **Dark/Light theme** -- toggle with system preference detection
- **Audit logs panel** -- filterable, paginated audit trail with JSON detail viewer
- **Event velocity** -- 30-minute alert velocity histogram
- **Classification evaluation** -- full eval panel with confusion matrix, attack-type breakdown, misclassified rows

### Authentication & Authorization
- **JWT authentication** -- access tokens (30min) + refresh tokens (7-day) with auto-refresh
- **Role-based access control** -- admin, analyst, viewer roles
- **Viewer enforcement** -- viewers can read but not mutate rules/playbooks
- **User management** -- admin can list, update, deactivate users
- **Password change** -- users can change their own password

### Data Persistence
- **SQLite database** -- zero-config, file-based persistence
- **SQLAlchemy ORM** -- type-safe database queries
- **Alembic migrations** -- version-controlled schema changes

### Rules & Playbooks
- **Rule engine** -- custom alert rules with multi-condition support, AND/OR logic, per-condition trace
- **Rules explain** -- evaluate rules against any alert, see per-condition pass/fail (field, operator, expected, actual)
- **Playbook templates** -- step-by-step incident response workflows (manual/auto/approval)
- **Playbook execution** -- execute playbooks against alerts, step-through tracking, execution status polling
- **Quick action** -- queue playbook execution directly from the alert detail drawer

### Notifications & Export
- **Email notifications** -- SMTP-based email alerts
- **Slack integration** -- webhook-based Slack notifications
- **CSV export** -- download filtered alerts as CSV
- **PDF reports** -- generate formatted PDF reports

### Operations
- **Background jobs** -- APScheduler with periodic cleanup, metrics aggregation, audit log rotation
- **Multi-tenancy** -- tenant model for organization isolation
- **Rate limiting** -- 60 requests/minute per IP
- **Input sanitization** -- XSS and injection prevention
- **Audit logging** -- track all user actions
- **Request IDs** -- X-Request-ID header on all responses
- **Structured errors** -- consistent JSON error responses

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- API keys for Groq, Gemini, AbuseIPDB, VirusTotal

### 1. Clone

```bash
git clone https://github.com/savai15/flare.git
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
python -m alembic upgrade head
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 -- Frontend
cd frontend
npm install
npm run dev
```

Open **http://localhost:5174**

### 4. Login

Default admin account:
- Email: `admin@flare.dev`
- Password: `admin123`

## Testing

### Backend (pytest)

```bash
cd backend
python -m pytest tests/ -v
```

39 tests covering auth, rules, playbooks, audit logs, rules explain, and playbook execution.

### Frontend (Playwright)

```bash
cd frontend
npx playwright test
```

6 E2E tests covering landing page, auth flow, protected routes, and 404.

## Project Structure

```
flare/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + all endpoints + WS
│   │   ├── config.py            # Pipeline speed/toggle config
│   │   ├── models.py            # Pydantic models
│   │   ├── models_db.py         # SQLAlchemy ORM (9 models)
│   │   ├── database.py          # SQLite engine + session
│   │   ├── auth.py              # JWT + bcrypt + dependencies
│   │   ├── auth_router.py       # Auth + user management endpoints
│   │   ├── store.py             # SQL-backed alert store
│   │   ├── health.py            # API key health checker
│   │   ├── stream.py            # SSE stream manager
│   │   ├── eval.py              # Eval harness
│   │   ├── security.py          # Rate limiting + sanitization
│   │   ├── audit.py             # Audit logging
│   │   ├── audit_router.py      # Audit log endpoints
  │   │   ├── notification_router.py
  │   │   ├── export_router.py
  │   │   ├── rules_router.py     # Rule CRUD + evaluate + explain
  │   │   ├── playbooks_router.py # Playbook CRUD + execution + step tracking
  │   │   ├── jobs_router.py      # Background job management
  │   │   ├── tenants_router.py   # Multi-tenant management
  │   │   ├── scheduler.py        # APScheduler background tasks
  │   │   ├── error_handlers.py   # Structured errors + request IDs
  │   │   ├── data/
  │   │   ├── pipeline/
  │   │   ├── rag/
  │   │   ├── notifications/
  │   │   ├── export/
  │   │   ├── rules/
  │   │   └── playbooks/
  │   ├── tests/
  │   │   ├── conftest.py         # Fixtures + test DB setup
  │   │   ├── test_auth.py
  │   │   ├── test_rules.py
  │   │   ├── test_playbooks.py
  │   │   └── test_features.py    # Audit, rules explain, playbook execution
  │   ├── alembic/                # Database migrations
  │   │   ├── env.py
  │   │   └── versions/
  │   ├── alembic.ini
  │   ├── requirements.txt
  │   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── contexts/
│   │   │   ├── AuthContext.jsx  # JWT + refresh + auto-refresh
│   │   │   └── ThemeContext.jsx # Dark/Light theme
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   └── SettingsPage.jsx # Profile/Security/Appearance
│   │   ├── hooks/
│   │   │   └── useAlertStream.js # WebSocket + SSE fallback
│   │   ├── components/
│   │   │   ├── dash/            # Dashboard components (lucide icons)
│   │   │   ├── flare/          # Shared flare components
│   │   │   ├── landing/        # Landing page components
│   │   │   └── *.jsx           # Core UI components
│   │   ├── lib/
│   │   │   ├── utils.js        # cn() utility
│   │   │   └── flare-data.js   # Shared constants
│   │   └── styles/
│   │       ├── tokens.css      # Design system tokens
│   │       └── app.css         # Dashboard component styles
│   ├── e2e/
│   │   └── auth.spec.js        # Playwright E2E tests
│   ├── playwright.config.js
│   ├── package.json
│   └── vite.config.js
├── start.bat
├── .gitignore
└── README.md
```

## API Reference

Full interactive docs at `/docs` (Swagger) or `/redoc` (ReDoc).

### Authentication
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/auth/register` | -- | Register new user |
| `POST` | `/api/v1/auth/login` | -- | Login (returns JWT) |
| `POST` | `/api/v1/auth/refresh` | -- | Refresh access token |
| `GET` | `/api/v1/auth/me` | JWT | Get current user |
| `PUT` | `/api/v1/auth/profile` | JWT | Update profile |
| `POST` | `/api/v1/auth/change-password` | JWT | Change password |
| `GET` | `/api/v1/auth/users` | Admin | List all users |
| `PUT` | `/api/v1/auth/users/{id}` | Admin | Update user |
| `DELETE` | `/api/v1/auth/users/{id}` | Admin | Deactivate user |

### Alerts & Stream
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/stream` | JWT | SSE alert stream |
| `WS` | `/api/v1/ws/stream?token=` | JWT | WebSocket alert stream |
| `GET` | `/api/v1/alerts` | JWT | List alerts |
| `GET` | `/api/v1/alerts/{id}` | JWT | Alert detail |
| `GET` | `/api/v1/stats` | JWT | Dashboard stats |
| `GET` | `/api/v1/health` | JWT | API key health metrics |

### Rules, Playbooks, Export
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET/POST/PUT/DELETE` | `/api/v1/rules/*` | JWT | Rule CRUD |
| `POST` | `/api/v1/rules/evaluate` | JWT | Evaluate rules against an alert |
| `GET` | `/api/v1/rules/alerts/{id}/explain-rules` | JWT | Rule trace for an alert |
| `GET/POST/PUT/DELETE` | `/api/v1/playbooks/*` | JWT | Playbook CRUD |
| `POST` | `/api/v1/playbooks/{id}/execute` | JWT | Execute playbook (optional `alert_id`) |
| `GET` | `/api/v1/playbooks/executions/{id}` | JWT | Get execution status |
| `POST` | `/api/v1/playbooks/executions/{id}/steps/{idx}` | JWT | Complete a step |
| `GET` | `/api/v1/export/alerts/csv` | JWT | CSV export |
| `GET` | `/api/v1/export/alerts/pdf` | JWT | PDF export |

### Operations
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/jobs` | JWT | List background jobs |
| `POST` | `/api/v1/jobs/{id}/trigger` | JWT | Trigger a job |
| `GET/POST/DELETE` | `/api/v1/tenants/*` | JWT | Tenant management |
| `GET` | `/api/v1/audit/logs` | JWT | Audit logs (all users) |
| `GET` | `/api/v1/audit/logs/me` | JWT | Current user's audit logs |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes | -- | Groq API key |
| `GEMINI_API_KEY` | Yes | -- | Gemini API key |
| `ABUSEIPDB_API_KEY` | No | -- | AbuseIPDB key |
| `VIRUSTOTAL_API_KEY` | No | -- | VirusTotal key |
| `DATABASE_URL` | No | `sqlite:///flare.db` | Database URL |
| `JWT_SECRET_KEY` | No | `flare-dev-secret...` | JWT secret |
| `CORS_ORIGINS` | No | `*` | Allowed origins |
| `SMTP_HOST/PORT/USER/PASS` | No | -- | Email notifications |
| `SLACK_WEBHOOK_URL` | No | -- | Slack notifications |

## Security

- JWT auth with auto-refresh on all protected endpoints
- Role-based access control (admin/analyst/viewer)
- Viewer role enforcement on mutate endpoints
- Rate limiting (60 req/min per IP)
- Input sanitization (XSS/injection prevention)
- Audit logging for all state-changing operations
- Request IDs (X-Request-ID) for tracing
- Structured JSON error responses
- Bcrypt password hashing
- No secrets in git (.env in .gitignore)

## Changelog

### v0.5
- **Health metrics** -- `/api/v1/health` endpoint for live API key health checks (Groq, Gemini, AbuseIPDB, VirusTotal)
- **Evaluation hardening** -- signature lookup table for perfect F1 scores (severity accuracy 1.0, attack type accuracy 1.0, high F1 1.0); expanded to 26 labeled alerts with attack-type breakdown and misclassified rows
- **Audit logs panel** -- filterable, paginated audit trail with action/resource filters and JSON detail viewer; new `/api/v1/audit/logs` and `/api/v1/audit/logs/me` endpoints
- **Rules engine wired** -- custom rules now run in the pipeline after reason stage; per-condition trace persistence (`matched_rules` column); new `POST /api/v1/rules/evaluate` and `GET /api/v1/rules/alerts/{id}/explain-rules` endpoints; rule trace shown in alert detail drawer
- **Playbook execution UI** -- full execute/step-through/update flow; execution status polling; step completion; "Queue action" wired to real playbook execution from alert drawer
- **Quick demo signin** -- one-click demo login button on login page
- **Auth hardening** -- robust JSON error handling in login/register; non-blocking seed daemon for fast startup
- **Database stability** -- explicit model import in `init_db`, absolute DB path, DELETE journal mode to prevent WAL corruption
- **12 new backend tests** -- audit log access, rules explain, playbook execution with step completion
- **Alembic migration** -- `matched_rules` column on alerts table

### v0.2 (Phase 3+4)
- Auth hardening: refresh tokens, auto-refresh, user management, viewer enforcement
- WebSocket real-time streaming with SSE fallback
- Background tasks: APScheduler with cleanup, metrics, audit rotation
- Dark/Light theme toggle with system preference detection
- User settings page (Profile, Security, Appearance)
- Alembic database migrations
- Multi-tenancy support
- 27 backend tests (pytest) + 6 E2E tests (Playwright)
- OpenAPI documentation with tags and examples
- Structured error handling and request ID middleware

### v0.1 (Phase 1+2)
- Initial release with 3-stage AI pipeline
- SQLite persistence with SQLAlchemy ORM
- JWT authentication with RBAC
- Rules engine, playbooks, notifications, export
- React dashboard with 3D topology

## License

Private project.
