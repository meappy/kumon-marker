#!/usr/bin/env bash
# Set up GitHub branch protection rules for main branch.
# Requires: gh CLI authenticated with admin access.
#
# Usage: ./scripts/setup-branch-protection.sh [owner/repo]

set -euo pipefail

REPO="${1:-meappy/kumon-marker}"

echo "Setting up branch protection for $REPO (main branch)..."

# Create branch protection ruleset via GitHub API
# Rulesets are the modern replacement for branch protection rules
gh api \
  --method POST \
  "repos/$REPO/rulesets" \
  --input - <<'EOF'
{
  "name": "Protect main",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["refs/heads/main"],
      "exclude": []
    }
  },
  "rules": [
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_status_checks_policy": true,
        "required_status_checks": [
          { "context": "Lint Backend" },
          { "context": "Lint Frontend" },
          { "context": "Lint Helm Charts" },
          { "context": "Build Test" }
        ]
      }
    },
    {
      "type": "deletion"
    },
    {
      "type": "non_fast_forward"
    }
  ]
}
EOF

echo "Branch protection ruleset created successfully."
echo ""
echo "Rules applied to main:"
echo "  - Require PR (no direct pushes)"
echo "  - Require passing status checks (Lint Backend, Lint Frontend, Lint Helm, Build Test)"
echo "  - Prevent branch deletion"
echo "  - Prevent force pushes"
