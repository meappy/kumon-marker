<p align="center">
  <img src="branding/banner.png" alt="Kumon Marker" width="700" />
</p>

<p align="center">
  <a href="https://github.com/meappy/kumon-marker/actions/workflows/release.yml"><img src="https://github.com/meappy/kumon-marker/actions/workflows/release.yml/badge.svg" alt="Release" /></a>
  <a href="https://github.com/meappy/kumon-marker/actions/workflows/ci.yml"><img src="https://github.com/meappy/kumon-marker/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" /></a>
</p>

Automated marking system for Kumon maths worksheets using pluggable vision AI providers.

## Features

- **Automatic worksheet marking** — Uses vision AI (Ollama, Anthropic Claude, Google Gemini, or OpenAI) to analyse and mark worksheets
- **PDF annotation** — Marks correct pages with green circles, errors with red ticks
- **Report generation** — Creates detailed PDF reports with scores and corrections
- **Google Drive integration** — Sync worksheets directly from Google Drive
- **Multi-user support** — Google OAuth authentication with per-user data isolation
- **Job queue** — RabbitMQ-based queue for reliable background processing
- **Kubernetes ready** — Helm charts with Argo CD GitOps deployment

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   FastAPI   │────▶│  RabbitMQ   │────▶│   Worker    │
│   (React)   │◀────│   (API)     │     │  (Queue)    │     │ (Processor) │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                                       │
                           ▼                                       ▼
                    ┌─────────────┐                         ┌─────────────┐
                    │ PostgreSQL  │                         │  Vision AI  │
                    │  (Jobs DB)  │                         │  Provider   │
                    └─────────────┘                         └─────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose (for local development)
- Kubernetes cluster with Helm (for production)
- Google Cloud project with OAuth configured
- Vision AI backend: Ollama (local), Google Gemini, Anthropic Claude, or OpenAI

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/meappy/kumon-marker.git
   cd kumon-marker
   ```

2. Create environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Start with Docker Compose:
   ```bash
   docker compose up -d
   ```

4. Access the app at http://localhost:3000

### Kubernetes Deployment

1. Create namespace:
   ```bash
   kubectl create namespace kumon-marker
   ```

2. Deploy with Helm:
   ```bash
   helm upgrade --install kumon-marker ./helm/kumon-marker \
     -f ./helm/kumon-marker/values.yaml \
     -f ./helm/kumon-marker/values-local.yaml \
     -n kumon-marker
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VISION_PROVIDER` | AI provider: `ollama`, `anthropic`, `gemini`, `openai` | `ollama` |
| `VALIDATION_METHOD` | Worksheet validation: `ocr` or `llm` | `ocr` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model name | `moondream` |
| `ANTHROPIC_API_KEY` | Anthropic API key or OAuth token | - |
| `ANTHROPIC_MODEL` | Anthropic model name | `claude-sonnet-4-20250514` |
| `GEMINI_API_KEY` | Google Gemini API key | - |
| `GEMINI_MODEL` | Gemini model name | `gemini-2.0-flash` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4o` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | - |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | - |
| `ALLOWED_USERS` | Comma-separated list of allowed emails | - |
| `SESSION_SECRET` | Secret for signing session cookies | - |
| `RABBITMQ_URL` | RabbitMQ connection URL | - |
| `DATABASE_URL` | PostgreSQL connection URL | - |

## Development

### Project Structure

```
kumon-marker/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── core/      # Config, session management
│   │   ├── models/    # Pydantic schemas, SQLAlchemy models
│   │   ├── routers/   # API endpoints
│   │   └── services/  # Business logic (providers, marking, etc.)
│   └── pyproject.toml
├── frontend/          # React + Vite + Tailwind CSS
│   ├── src/
│   │   ├── api/       # API client
│   │   ├── components/# React components
│   │   └── utils/     # Helper functions
│   └── package.json
├── helm/              # Kubernetes Helm charts
│   └── kumon-marker/
├── branding/          # Logo, favicon, banner assets
├── scripts/           # Development scripts
│   └── version.py     # Version management
├── Dockerfile         # Multi-stage Docker build
└── VERSION            # Current version
```

### CI/CD & GitOps

This project uses **Semantic Release** for automated versioning and **Argo CD** for GitOps deployments.

```bash
# Feature branch → builds dev image
git checkout -b feat/my-feature
git commit -m "feat: add new feature"
git push origin feat/my-feature

# Merge to main → auto version bump + deploy
# fix: commits → patch (0.6.2 → 0.6.3)
# feat: commits → minor (0.6.2 → 0.7.0)
# BREAKING CHANGE: → major (0.6.2 → 1.0.0)
```

### Version Management

All version numbers are kept in sync across files:

```bash
# Show current versions
./scripts/version.py show

# Bump version
./scripts/version.py bump patch    # Bug fix
./scripts/version.py bump minor    # Feature
./scripts/version.py bump major    # Breaking change

# Sync all files to VERSION
./scripts/version.py sync
```

### Building

```bash
# Build Docker image
docker build -t ghcr.io/meappy/kumon-marker:latest .
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/status` | Get authentication status |
| POST | `/api/auth/login` | Initiate Google OAuth login |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/worksheets` | List marked worksheets |
| POST | `/api/worksheets/{id}/process` | Queue worksheet for marking |
| GET | `/api/worksheets/{id}/marked` | Download marked PDF |
| GET | `/api/worksheets/{id}/report` | Download report PDF |
| GET | `/api/gdrive/files` | List Google Drive files |
| POST | `/api/gdrive/sync/{id}` | Sync file from Google Drive |
| GET | `/api/jobs/status` | Get job queue status |
| DELETE | `/api/jobs/{id}` | Cancel a job |

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for how to fork, set up your environment, and submit a pull request.

## License

MIT License — see [LICENSE](LICENSE) for details.
