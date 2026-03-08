# Contributing to Kumon Marker

Thanks for your interest in contributing! This guide covers how to get started.

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repo on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/kumon-marker.git
cd kumon-marker

# Add the upstream remote
git remote add upstream https://github.com/meappy/kumon-marker.git
```

### 2. Set Up Development Environment

**Backend (Python 3.12+)**

```bash
cd backend
uv pip install --system -e .
uvicorn app.main:app --reload    # Runs on port 8000
```

**Frontend (Node.js 18+)**

```bash
cd frontend
npm ci
npm run dev                       # Runs on port 5173
```

**Full stack with Docker**

```bash
cp .env.example .env              # Edit with your settings
docker compose up -d
```

### 3. Create a Branch

Always work on a feature branch, never commit directly to `main`.

```bash
# Sync with upstream first
git fetch upstream
git checkout -b feat/my-feature upstream/main
```

Branch naming conventions:
- `feat/description` — New features
- `fix/description` — Bug fixes
- `docs/description` — Documentation changes
- `refactor/description` — Code refactoring

## Making Changes

### Code Style

- **Backend**: Python code is linted with [Ruff](https://github.com/astral-sh/ruff). Run `ruff check .` before committing.
- **Frontend**: TypeScript/React code is linted with ESLint. Run `npm run lint` before committing.
- **Spelling**: Use British English throughout (e.g. "analyse", "colour", "initialise").

### Commit Messages

This project uses [Semantic Release](https://github.com/semantic-release/semantic-release), so commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
feat: add support for new vision provider
fix: correct score calculation for multi-page worksheets
docs: update API endpoint documentation
refactor: simplify worksheet validation logic
```

- `fix:` — Triggers a patch version bump (e.g. 1.0.1 → 1.0.2)
- `feat:` — Triggers a minor version bump (e.g. 1.0.1 → 1.1.0)
- `BREAKING CHANGE:` in the commit body — Triggers a major version bump

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run lint

# Helm charts
helm lint helm/kumon-marker/
```

## Submitting a Pull Request

1. Push your branch to your fork:
   ```bash
   git push origin feat/my-feature
   ```

2. Open a pull request against `main` on the upstream repo.

3. In the PR description:
   - Summarise what the change does and why
   - Note any breaking changes
   - Include steps to test the change

4. CI will run linting automatically. Make sure all checks pass.

## Project Structure

```
kumon-marker/
├── backend/           # FastAPI backend (Python)
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
├── branding/          # Logo, favicon, banner assets
├── scripts/           # Development scripts
├── Dockerfile         # Multi-stage Docker build
└── VERSION            # Current version
```

## Key Concepts

- **Vision Providers**: All AI providers implement the `VisionProvider` ABC in `backend/app/services/providers.py`. To add a new provider, create a new class implementing this interface.
- **Processing Pipeline**: Upload → Validate → Queue (RabbitMQ) → Worker → Analyse → Annotate → Report
- **Kumon Sheet IDs**: Follow the pattern letter + digits + a/b suffix (e.g. `B161a`, `D166b`)

## Need Help?

- Open an [issue](https://github.com/meappy/kumon-marker/issues) for bugs or feature requests
- Check existing issues before creating a new one
