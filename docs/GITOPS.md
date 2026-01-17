# GitOps CI/CD Workflow

This project uses **Semantic Release** for automated versioning and **Argo CD** for GitOps deployments.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Feature Branch │────▶│   GitHub Actions │────▶│     GHCR        │
│     Push        │     │   (CI Build)     │     │  branch-<name>  │
└─────────────────┘     └─────────────────┘     └─────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   PR Merge to   │────▶│ Semantic Release │────▶│  GitHub Actions │────▶│     GHCR        │
│      main       │     │  (Auto Version)  │     │  (Docker Build) │     │    v0.3.0       │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
                                │                                              │
                                ▼                                              │
                        ┌─────────────────┐                                    │
                        │ values-argocd.yaml │                                   │
                        │   tag: "0.3.0"   │                                   │
                        └─────────────────┘                                    │
                                │                                              │
                                ▼                                              │
                        ┌─────────────────┐     ┌─────────────────┐            │
                        │    Argo CD      │────▶│   Kubernetes    │◀───────────┘
                        │  (Auto Sync)    │     │   Deployment    │
                        └─────────────────┘     └─────────────────┘
```

## Workflow

### 1. Feature Development (Branch Builds)

When you push to any branch (except `main`):

```bash
git checkout -b feature/my-feature
# Make changes
git commit -m "feat: add new feature"
git push origin feature/my-feature
```

**GitHub Actions (ci.yml):**
- Runs linting (backend + frontend)
- Builds Docker image
- Pushes to GHCR as `ghcr.io/meappy/kumon-marker:branch-feature-my-feature`

**Testing branch builds:**
```bash
# Temporarily deploy branch image for testing
helm upgrade kumon-marker ./helm/kumon-marker \
  -f ./helm/kumon-marker/values-local.yaml \
  --set image.tag=branch-feature-my-feature \
  -n kumon-marker
```

### 2. Release (Merge to main)

When you merge a PR to `main`:

```bash
git checkout main
git merge feature/my-feature
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

### 3. Automatic Deployment (Argo CD)

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

### `argocd/application.yaml`
Argo CD Application manifest - defines source repo, target namespace, sync policy.

### `argocd/repo-secret.yaml`
GitHub credentials for Argo CD to access private repo (not committed to git).

## Manual Operations

### Check Argo CD Status
```bash
kubectl get application -n argocd kumon-marker
```

### Force Sync
```bash
kubectl delete application -n argocd kumon-marker
kubectl apply -f argocd/application.yaml
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

Sensitive values are stored in Kubernetes Secret `kumon-marker-secrets`, not in git.

The Helm chart uses `existingSecret` to reference this pre-created secret:
```yaml
# values-argocd.yaml
existingSecret: "kumon-marker-secrets"
```

To update secrets:
```bash
kubectl edit secret kumon-marker-secrets -n kumon-marker
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
