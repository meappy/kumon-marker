# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kumon Marker is an automated marking system for Kumon maths worksheets. It uses pluggable vision AI providers (Ollama, Anthropic, Google Gemini, or OpenAI) to analyse scanned PDF worksheets, mark answers, annotate PDFs, and generate reports.

## Architecture

- **Frontend**: React + Vite + Tailwind CSS (in `frontend/`), served as static files by the backend
- **Backend**: FastAPI (Python 3.12) in `backend/`, the API server and static file host
- **Worker**: RabbitMQ consumer (`backend/app/worker.py`) that processes worksheet marking jobs asynchronously
- **Database**: PostgreSQL for job tracking (SQLAlchemy ORM), optional (queue features disabled without it)
- **Queue**: RabbitMQ for job dispatch between API and worker
- **Deployment**: Kubernetes via Helm charts + Argo CD GitOps; Docker multi-stage build

The API server and worker run as separate containers from the same codebase. The API publishes jobs to RabbitMQ; the worker consumes them.

## Common Commands

### Backend
```bash
cd backend
uv pip install --system -e .          # Install dependencies
uvicorn app.main:app --reload         # Run dev server (port 8000)
python -m app.worker                  # Run the RabbitMQ worker
ruff check .                          # Lint Python code
pytest                                # Run tests (dev dependency)
```

### Frontend
```bash
cd frontend
npm ci                                # Install dependencies
npm run dev                           # Vite dev server
npm run build                         # Production build (tsc + vite)
npm run lint                          # ESLint
```

### Docker & Helm
```bash
docker build -t kumon-marker:local .
docker compose up -d                  # Local dev with all services
helm lint helm/kumon-marker/          # Lint Helm chart
helm template kumon-marker helm/kumon-marker/  # Test template rendering
```

### Version Management
```bash
./scripts/version.py show             # Show current version across all files
./scripts/version.py bump patch       # Bump patch version
./scripts/version.py sync             # Sync all files to VERSION
```

## Key Processing Pipeline

1. **Upload/Sync** — PDF uploaded via UI or synced from Google Drive (`From_BrotherDevice` folder)
2. **Validation** (`services/checker.py`) — Confirms PDF is a Kumon worksheet, extracts sheet ID (e.g. `D166a`) via text layer, OCR or LLM (configurable)
3. **Job Queue** (`services/queue.py`) — Creates a Job record in PostgreSQL and publishes to RabbitMQ
4. **Worker** (`worker.py`) — Consumes job, runs the pipeline:
   - Extracts student name via vision provider (`services/ocr.py:extract_name_with_vision`)
   - Analyses each page with vision AI (`services/ocr.py:analyse_worksheet`) — returns JSON with errors per page
   - Annotates the PDF (`services/annotator.py`) — green circle for all-correct pages, red ticks for errors
   - Generates a report PDF (`services/reporter.py`)
5. **Download** — User downloads marked PDF and report from the UI

## Vision AI Providers

Controlled by `VISION_PROVIDER` env var (or runtime settings via UI). All providers implement the `VisionProvider` ABC in `services/providers.py`:

- `ollama` (default) — Local LLM via Ollama API, no rate limits
- `anthropic` — Anthropic API (supports both API keys and OAuth session tokens)
- `gemini` — Google Gemini API (google-genai SDK)
- `openai` — OpenAI API (GPT-4o, etc.)

Anthropic OAuth tokens (prefix `sk-ant-oat01-`) are auto-detected and use Bearer auth with the `anthropic-beta` header.

### Validation Method

Controlled by `VALIDATION_METHOD` env var:
- `ocr` (default) — Tesseract OCR for sheet ID extraction (fast, free)
- `llm` — Vision provider for sheet ID extraction (more robust for scanned PDFs)

`VALIDATION_PROVIDER` optionally overrides which provider is used for validation (defaults to the main `VISION_PROVIDER`).

## CI/CD and Versioning

- **Semantic Release** on `main` branch: commit prefixes (`fix:`, `feat:`, `BREAKING CHANGE:`) trigger version bumps
- Version is kept in sync across `VERSION`, `frontend/package.json`, `backend/pyproject.toml`, `backend/app/core/config.py`, and `helm/kumon-marker/Chart.yaml` via `scripts/version.py`
- **Feature branches** (`fix/**`, `feat/**`, `feature/**`): CI builds Docker image, force-pushes to `dev` branch, triggers Argo CD sync
- **Main branch**: semantic-release bumps version, builds + pushes tagged Docker image, triggers Argo CD sync
- Linting: `ruff` for backend, `eslint` for frontend, `helm lint` for charts (all run in CI)
- Branch protection: `./scripts/setup-branch-protection.sh` configures GitHub rulesets for main

## Configuration

Settings are managed via `backend/app/core/config.py` using pydantic-settings. Key env vars:

| Variable | Description | Default |
|---|---|---|
| `VISION_PROVIDER` | AI provider: `ollama`, `anthropic`, `gemini`, `openai` | `ollama` |
| `VALIDATION_METHOD` | Worksheet validation: `ocr` or `llm` | `ocr` |
| `VALIDATION_PROVIDER` | Override provider for validation (empty = same as VISION_PROVIDER) | `""` |
| `ANTHROPIC_API_KEY` | API key or OAuth token (`sk-ant-oat01-...`) | |
| `GEMINI_API_KEY` | Google Gemini API key | |
| `OPENAI_API_KEY` | OpenAI API key | |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://host.docker.internal:11434` |

Legacy `CLAUDE_MODE` env var is still supported and mapped automatically (`api` → `anthropic`, `cli` → `anthropic`).

Runtime overrides are stored in `{DATA_DIR}/settings.json` and take precedence over env vars.

## Conventions

- British English spelling throughout (e.g. "analyse", "colour", "initialise")
- Kumon sheet IDs follow the pattern: letter + digits + a/b suffix (e.g. `B161a`, `D166b`)
- Per-user data isolation: each user's files stored under `{DATA_DIR}/{user_id}/`
- The `data/` directory structure: `scans/`, `marked/`, `reports/`, `results/`
