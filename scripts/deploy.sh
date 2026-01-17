#!/bin/bash
# Deploy Kumon Marker to Kubernetes
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "==> Building Docker image..."
docker build -t kumon-marker:latest .

echo "==> Deploying to Kubernetes..."
helm upgrade --install kumon-marker ./helm/kumon-marker \
  -f ./helm/kumon-marker/values-local.yaml \
  ${ANTHROPIC_API_KEY:+--set config.anthropic.apiKey="$ANTHROPIC_API_KEY"}

echo "==> Waiting for deployment..."
kubectl rollout status deployment/kumon-marker --timeout=120s

echo "==> Deployment complete!"
echo ""
kubectl get pods -l app.kubernetes.io/name=kumon-marker
echo ""
echo "Access the UI at: http://$(hostname -I | awk '{print $1}'):30080"
