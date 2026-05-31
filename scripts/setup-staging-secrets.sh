#!/usr/bin/env bash
# Upload STAGING_* GitHub Actions secrets from a local env file.
#
# Usage:
#   cp staging.env.example .env.staging
#   # edit .env.staging with real values
#   ./scripts/setup-staging-secrets.sh .env.staging
#
# Requires: gh CLI authenticated against the dddictionary/4brar.me repo.

set -euo pipefail

ENV_FILE="${1:-.env.staging}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: env file not found: $ENV_FILE" >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh CLI not installed" >&2
  exit 1
fi

while IFS='=' read -r key value; do
  [[ -z "$key" || "$key" =~ ^# ]] && continue
  value="${value%\"}"
  value="${value#\"}"
  if [[ -z "$value" ]]; then
    echo "skip $key (empty)"
    continue
  fi
  echo "set $key"
  gh secret set "$key" --body "$value"
done < "$ENV_FILE"

echo "done."
