#!/usr/bin/env bash
# git-mirror-push.sh — mirror new commits from main → ameri-main and push both remotes
set -euo pipefail

export MIRROR_PUSH_RUNNING=1

cd "$(git rev-parse --show-toplevel)"

CURRENT=$(git symbolic-ref --short HEAD)
if [ "$CURRENT" != "main" ]; then
  echo "✗ Refusing: must be on 'main' (currently on '$CURRENT')." >&2
  exit 1
fi

if ! git diff-index --quiet HEAD --; then
  echo "✗ Refusing: working tree has uncommitted changes." >&2
  exit 1
fi

for ref in refs/heads/ameri-main refs/remotes/legacy/main refs/remotes/ameri/main; do
  if ! git rev-parse --verify --quiet "$ref" >/dev/null; then
    echo "✗ Missing required ref: $ref" >&2
    exit 1
  fi
done

if ! git rev-parse --verify --quiet refs/mirror/last-synced >/dev/null; then
  echo "✗ Missing baseline ref refs/mirror/last-synced." >&2
  echo "  Bootstrap with: git update-ref refs/mirror/last-synced main" >&2
  exit 1
fi

LAST_SYNCED=$(git rev-parse refs/mirror/last-synced)

mapfile -t PENDING < <(git rev-list --reverse "${LAST_SYNCED}..main")

if [ "${#PENDING[@]}" -gt 0 ]; then
  echo "→ ${#PENDING[@]} commit(s) to mirror onto ameri-main:"
  for sha in "${PENDING[@]}"; do
    git --no-pager log --oneline -1 "$sha"
  done
  echo

  git checkout ameri-main

  for sha in "${PENDING[@]}"; do
    echo "  cherry-pick $sha"
    if ! git cherry-pick --allow-empty --keep-redundant-commits "$sha"; then
      echo "✗ Cherry-pick failed at $sha. Resolve, then run:" >&2
      echo "    git cherry-pick --continue" >&2
      echo "    git checkout main && bash scripts/git-mirror-push.sh" >&2
      exit 1
    fi
  done

  git checkout main
else
  echo "→ ameri-main is already up-to-date with main."
fi

echo
echo "→ pushing main → legacy"
git push legacy main

echo
echo "→ pushing ameri-main → ameri"
git push ameri ameri-main:main

git update-ref refs/mirror/last-synced main
echo
echo "✓ Both repos in sync. Baseline updated to $(git rev-parse --short main)."
