#!/usr/bin/env bash
# Clone or update the ML pipeline repo from GitHub (no local src/ mount).
set -euo pipefail

REPO_DIR="${ML_REPO_DIR:-/opt/airflow/ml-repo}"
REPO_URL="${GITHUB_REPO_URL:?Set GITHUB_REPO_URL in airflow/.env}"
BRANCH="${GIT_BRANCH:-main}"

if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  REPO_URL="${REPO_URL/https:\/\//https://${GITHUB_TOKEN}@}"
fi

echo "Syncing ${REPO_URL} (branch ${BRANCH}) -> ${REPO_DIR}"

if [[ -d "${REPO_DIR}/.git" ]]; then
  git -C "${REPO_DIR}" fetch --depth 1 origin "${BRANCH}"
  git -C "${REPO_DIR}" checkout "${BRANCH}"
  git -C "${REPO_DIR}" reset --hard "origin/${BRANCH}"
else
  git clone --branch "${BRANCH}" --depth 1 "${REPO_URL}" "${REPO_DIR}"
fi

echo "Code at commit: $(git -C "${REPO_DIR}" rev-parse --short HEAD)"
