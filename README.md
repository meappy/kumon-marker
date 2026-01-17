# Kumon Marker

Automated marking system for Kumon worksheets using vision AI models.

## Features

- **Automatic worksheet marking** - Uses vision AI (Ollama/Gemini/Claude) to analyse and mark worksheets
- **Google Drive integration** - Sync worksheets directly from Google Drive
- **Report generation** - Creates detailed PDF reports with scores and corrections
- **Multi-user support** - Google OAuth authentication with per-user data isolation
- **Job queue** - RabbitMQ-based queue for reliable background processing
- **Kubernetes ready** - Helm charts for easy deployment

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   FastAPI   │────▶│  RabbitMQ   │────▶│   Worker    │
│   (React)   │◀────│   (API)     │     │  (Queue)    │     │ (Processor) │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                                       │
                           ▼                                       ▼
                    ┌─────────────┐                         ┌─────────────┐
                    │ PostgreSQL  │◀────────────────────────│   SQLite    │
                    │  (Jobs DB)  │                         │  (Updates)  │
                    └─────────────┘                         └─────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose (for local development)
- Kubernetes cluster with Helm (for production)
- Google Cloud project with OAuth configured
- Vision AI backend: Ollama (local), Google Gemini, or Anthropic Claude

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

2. Create secrets:
   ```bash
   kubectl create secret generic kumon-marker-secrets \
     --from-literal=google-client-id=YOUR_CLIENT_ID \
     --from-literal=google-client-secret=YOUR_CLIENT_SECRET \
     --from-literal=session-secret=YOUR_SESSION_SECRET \
     -n kumon-marker
   ```

3. Deploy with Helm:
   ```bash
   helm upgrade --install kumon-marker ./helm/kumon-marker \
     -f ./helm/kumon-marker/values.yaml \
     -n kumon-marker
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CLAUDE_MODE` | AI backend: `ollama`, `gemini`, `api`, `cli` | `ollama` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model name | `moondream` |
| `GEMINI_API_KEY` | Google Gemini API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
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
│   │   └── services/  # Business logic (OCR, marking, etc.)
│   └── pyproject.toml
├── frontend/          # React frontend
│   ├── src/
│   │   ├── api/       # API client
│   │   ├── components/# React components
│   │   └── utils/     # Helper functions
│   └── package.json
├── helm/              # Kubernetes Helm charts
│   └── kumon-marker/
├── scripts/           # Development scripts
│   ├── version.py     # Version management
│   └── deploy.sh      # Deployment helper
├── Dockerfile         # Multi-stage Docker build
└── VERSION            # Current version
```

### Version Management

All version numbers are kept in sync across files:

```bash
# Show current versions
./scripts/version.py show

# Bump version
./scripts/version.py bump patch    # Bug fix: 0.2.4 -> 0.2.5
./scripts/version.py bump minor    # Feature: 0.2.4 -> 0.3.0
./scripts/version.py bump major    # Breaking: 0.2.4 -> 1.0.0

# Set specific version
./scripts/version.py set 1.0.0

# Sync all files to VERSION
./scripts/version.py sync
```

### Building

```bash
# Build Docker image
docker build -t ghcr.io/meappy/kumon-marker:latest .

# Build with specific version
docker build --build-arg VERSION=0.2.4 -t ghcr.io/meappy/kumon-marker:0.2.4 .
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

## License

MIT License - see [LICENSE](LICENSE) for details.
