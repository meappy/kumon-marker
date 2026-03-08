# GitOps CI/CD Workflow

This project uses **Semantic Release** for automated versioning and **Argo CD** for GitOps deployments.

## Architecture

All branches (main + feature) deploy to the **same** `kumon-marker` namespace with the **same** deployment name. Pushing to a branch automatically deploys it, replacing whatever was running before.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Push to any   │────▶│   GitHub Actions │────▶│     GHCR        │────▶│  ApplicationSet │
│   branch        │     │   (CI Build)     │     │   image:tag     │     │  (Auto Deploy)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
                                                                               │
                               ┌───────────────────────────────────────────────┘
                               │
                               ▼
                       ┌─────────────────┐     ┌─────────────────┐
                       │    Argo CD      │────▶│   Kubernetes    │
                       │ kumon-marker-X  │     │  kumon-marker   │  (same deployment)
                       └─────────────────┘     └─────────────────┘

Branches:
  main           → kumon-marker-main         → image: 0.3.0 (semantic release)
  fix/bug        → kumon-marker-fix-bug      → image: branch-fix-bug
  feat/feature   → kumon-marker-feat-feature → image: branch-feat-feature
```

**Key point:** All branches deploy to the same Kubernetes resources. The last branch pushed "wins".

## Workflow

### 1. Feature Development (Automatic Branch Deployments)

When you push to a branch matching `fix/*`, `feat/*`, or `feature/*`:

```bash
git checkout -b fix/scanned-pdf-validation
# Make changes
git commit -m "fix: handle scanned PDFs without text layer"
git push origin fix/scanned-pdf-validation
```

**What happens automatically:**

1. **GitHub Actions (ci.yml):**
   - Runs linting (backend + frontend)
   - Builds Docker image
   - Pushes to GHCR as `ghcr.io/meappy/kumon-marker:branch-fix-scanned-pdf-validation`
   - Updates `values-argocd.yaml` in the branch with the new image tag
   - Commits and pushes to the branch

2. **Argo CD ApplicationSet:**
   - Detects the new branch matching `fix/*` pattern
   - Creates a new Application: `kumon-marker-fix-scanned-pdf-validation`
   - Deploys to namespace: `kumon-marker-fix-scanned-pdf-validation`
   - Auto-syncs whenever you push changes

3. **When you delete the branch:**
   - ApplicationSet automatically deletes the Application
   - Kubernetes namespace is cleaned up

**Check your branch deployment:**
```bash
# List branch deployments
kubectl get applications -n argocd | grep kumon-marker

# Check specific branch
kubectl get application -n argocd kumon-marker-fix-scanned-pdf-validation

# View pods in branch namespace
kubectl get pods -n kumon-marker-fix-scanned-pdf-validation
```

### 2. Release (Merge to main)

When you merge a PR to `main`:

```bash
git checkout main
git merge fix/scanned-pdf-validation
git push origin main
```

**GitHub Actions (release.yml):**

1. **Semantic Release** analyses commits and determines version bump:
   - `fix:` commits → **patch** (0.2.8 → 0.2.9)
   - `feat:` commits → **minor** (0.2.8 → 0.3.0)
   - `BREAKING CHANGE:` → **major** (0.2.8 → 1.0.0)

2. **Semantic Release** then:
   - Updates `VERSION`, `package.json`, `pyproject.toml`, `Chart.yaml`
   - Updates `values-argocd.yaml` with new image tag
   - Generates `CHANGELOG.md`
   - Commits changes with `[skip ci]`
   - Creates git tag (e.g., `v0.3.0`)
   - Creates GitHub Release

3. **Docker Build** (if new version):
   - Builds multi-arch image (amd64 + arm64)
   - Pushes to GHCR as `ghcr.io/meappy/kumon-marker:0.3.0` and `:latest`

### 3. Automatic Production Deployment (Argo CD)

Argo CD watches the `main` branch and auto-syncs when `values-argocd.yaml` changes:

1. Detects `values-argocd.yaml` has new `image.tag`
2. Runs `helm template` with updated values
3. Applies changes to Kubernetes
4. Deployment pulls new image from GHCR

## Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**
| Type | Version Bump | Description |
|------|--------------|-------------|
| `fix` | Patch | Bug fixes |
| `feat` | Minor | New features |
| `docs` | None | Documentation only |
| `style` | None | Code style (formatting) |
| `refactor` | None | Code refactoring |
| `perf` | Patch | Performance improvements |
| `test` | None | Adding tests |
| `chore` | None | Maintenance tasks |

**Breaking Changes:**
```
feat: change API response format

BREAKING CHANGE: The /api/worksheets endpoint now returns paginated results
```

## Configuration Files

### `.releaserc.json`
Semantic Release configuration - defines plugins and version update commands.

### `helm/kumon-marker/values-argocd.yaml`
Production values for Argo CD. Contains `image.tag` which is auto-updated.

### `argocd/applicationset.yaml`
Argo CD ApplicationSet that manages ALL deployments (main + feature branches). Creates an Application for each branch matching `main`, `fix/*`, `feat/*`, `feature/*`. All deployments use the same Helm release name (`kumon-marker`) so they deploy to the same resources.

### `argocd/repo-secret.yaml`
GitHub credentials for Argo CD to access private repo (not committed to git).

## Setup

### Install ApplicationSet

```bash
# Apply the ApplicationSet (one-time setup)
kubectl apply -f argocd/applicationset.yaml
```

### Create Repository Secret (for private repos)

```bash
# Create secret from template
cp argocd/repo-secret.yaml.example argocd/repo-secret.yaml
# Edit with your GitHub token
kubectl apply -f argocd/repo-secret.yaml
```

## Manual Operations

### Check Argo CD Status
```bash
# Production
kubectl get application -n argocd kumon-marker

# All applications (including branch deployments)
kubectl get applications -n argocd
```

### Force Sync
```bash
# Refresh the ApplicationSet
kubectl apply -f argocd/applicationset.yaml

# Or delete and recreate a specific application
kubectl delete application -n argocd kumon-marker-main
# ApplicationSet will automatically recreate it
```

### Access Argo CD UI
```bash
# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d

# UI available at https://<node-ip>:30443
# Username: admin
```

### Manual Version Bump (without commits)
```bash
# Bump and update all files including values-argocd.yaml
./scripts/version.py --values-file helm/kumon-marker/values-argocd.yaml bump patch
```

### Rollback
```bash
# Option 1: Revert in git (triggers new release)
git revert HEAD
git push origin main

# Option 2: Manual helm rollback
helm rollback kumon-marker -n kumon-marker

# Option 3: Update values-argocd.yaml to previous version
# Edit helm/kumon-marker/values-argocd.yaml, set tag to previous version
# Commit and push - Argo CD will sync
```

## Secrets Management

Sensitive values are supplied via a private secrets repository using ArgoCD multi-source, not stored in this repo.

The Helm chart supports two modes:
1. **Inline secrets** — supplied via a separate values file (e.g. from a private secrets repo)
2. **Existing secret** — reference a pre-created Kubernetes Secret via `existingSecret`

```yaml
# values-argocd.yaml
existingSecret: "my-secrets"  # or leave empty to use inline secrets
```

## Troubleshooting

### Argo CD shows "Unknown" sync status
```bash
# Check for errors
kubectl get application -n argocd kumon-marker -o jsonpath='{.status.conditions[*].message}'

# Restart repo server to refresh credentials
kubectl rollout restart deployment argocd-repo-server -n argocd
```

### Semantic Release not creating new version
- Ensure commits follow conventional format
- Check that commits since last tag include `fix:` or `feat:`
- View release workflow logs in GitHub Actions

### Image not updating in deployment
```bash
# Check current image
kubectl get deployment kumon-marker -n kumon-marker -o jsonpath='{.spec.template.spec.containers[0].image}'

# Check Argo CD sync status
kubectl get application -n argocd kumon-marker
```

### Branch deployment not created
```bash
# Check ApplicationSet status
kubectl get applicationset -n argocd kumon-marker

# Check if branch matches pattern (main, fix/*, feat/*, feature/*)
# Other branch names won't get auto-deployed

# View ApplicationSet events
kubectl describe applicationset -n argocd kumon-marker
```
