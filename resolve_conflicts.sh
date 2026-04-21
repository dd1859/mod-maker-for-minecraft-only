#!/usr/bin/env bash
set -euo pipefail

# Helper for resolving PR merge conflicts against a base branch.
# Usage:
#   ./resolve_conflicts.sh origin main
#   ./resolve_conflicts.sh upstream master

REMOTE="${1:-origin}"
BASE_BRANCH="${2:-main}"

if ! git remote | grep -qx "$REMOTE"; then
  echo "error: remote '$REMOTE' not found"
  echo "add one first, e.g. git remote add origin <repo-url>"
  exit 1
fi

git fetch "$REMOTE" "$BASE_BRANCH"

echo "Merging $REMOTE/$BASE_BRANCH into $(git rev-parse --abbrev-ref HEAD)..."
set +e
git merge "$REMOTE/$BASE_BRANCH"
MERGE_RC=$?
set -e

if [[ $MERGE_RC -eq 0 ]]; then
  echo "No conflicts. Merge completed."
  exit 0
fi

echo
echo "Merge reported conflicts. Unmerged files:"
git diff --name-only --diff-filter=U || true

echo
echo "Conflict markers still present in:"
rg -n '^(<<<<<<<|=======|>>>>>>>)' . || true

echo
echo "Resolve files, then run:"
echo "  git add <resolved-files>"
echo "  git commit"
