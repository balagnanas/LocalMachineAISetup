#!/usr/bin/env bash
# new-session.sh — start a fresh session: create a feature branch + dedicated git worktree.
#
# Usage (run from inside any git repository):
#   new-session.sh                 # pick a random <adjective>-<noun> name
#   new-session.sh my-feature      # use the suffix you supply
#
# Environment overrides:
#   SESSION_PREFIX   branch prefix (no trailing dash)   (default: sanitized git user.name, else "session")
#   SESSION_BASE     base branch, without "origin/"     (default: repo default branch, else dev/main/master)
#   SESSION_ROOT     worktree root directory            (default: <repo>/.worktrees)
#
# Behaviour:
#   1. Fetch origin.
#   2. Branch off origin/<SESSION_BASE> as <SESSION_PREFIX>-<adjective>-<noun>.
#   3. Add a git worktree under <SESSION_ROOT>/<branch>.
#   4. Print next steps.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -z "$REPO_ROOT" ]; then
  echo "error: not inside a git repository" >&2
  exit 1
fi
cd "$REPO_ROOT"

bold() { printf '\033[1m%s\033[0m\n' "$1"; }
warn() { printf '\033[33m%s\033[0m\n' "$1" >&2; }
err()  { printf '\033[31m%s\033[0m\n' "$1" >&2; }
ok()   { printf '\033[32m%s\033[0m\n' "$1"; }

# ---- base branch ---------------------------------------------------------
if [ -z "${SESSION_BASE:-}" ]; then
  SESSION_BASE="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##' || true)"
  if [ -z "$SESSION_BASE" ]; then
    for b in dev main master; do
      if git rev-parse --verify "origin/$b" >/dev/null 2>&1; then SESSION_BASE="$b"; break; fi
    done
  fi
  [ -n "$SESSION_BASE" ] || SESSION_BASE="dev"
fi

# ---- branch prefix -------------------------------------------------------
if [ -z "${SESSION_PREFIX:-}" ]; then
  SESSION_PREFIX="$(git config user.name 2>/dev/null \
    | tr '[:upper:]' '[:lower:]' \
    | sed 's/[^a-z0-9]/-/g; s/-\+/-/g; s/^-//; s/-$//' || true)"
  [ -n "$SESSION_PREFIX" ] || SESSION_PREFIX="session"
fi

# ---- worktree root -------------------------------------------------------
[ -n "${SESSION_ROOT:-}" ] || SESSION_ROOT="$REPO_ROOT/.worktrees"

# ---- fetch & validate ----------------------------------------------------
bold "Fetching origin..."
git fetch --quiet origin || { err "git fetch origin failed"; exit 1; }

if ! git rev-parse --verify "origin/$SESSION_BASE" >/dev/null 2>&1; then
  err "origin/$SESSION_BASE not found; set SESSION_BASE to an existing branch."
  exit 1
fi

mkdir -p "$SESSION_ROOT"

# ---- branch name ---------------------------------------------------------
ADJECTIVES=(amber bold calm eager frost gentle honest ivory jade kind lively noble opal quiet ruby steady swift vivid wise)
NOUNS=(badger crane dune falcon grove heron ibis kelp lotus maple newt otter pine quail robin sage talon ursa vine whale)

suffix="${1:-}"
branch=""
attempt=0
while :; do
  attempt=$((attempt + 1))
  if [ -n "$suffix" ]; then
    branch="${SESSION_PREFIX}-${suffix}"
  else
    adj="${ADJECTIVES[$((RANDOM % ${#ADJECTIVES[@]}))]}"
    noun="${NOUNS[$((RANDOM % ${#NOUNS[@]}))]}"
    branch="${SESSION_PREFIX}-${adj}-${noun}"
  fi

  exists=0
  git rev-parse --verify "$branch" >/dev/null 2>&1 && exists=1
  git ls-remote --exit-code origin "$branch" >/dev/null 2>&1 && exists=1

  if [ "$exists" -eq 0 ]; then break; fi
  if [ -n "$suffix" ] || [ "$attempt" -ge 20 ]; then
    err "Branch '$branch' already exists; choose a different suffix."
    exit 1
  fi
  warn "Branch '$branch' already exists — retrying with a new name..."
done

# ---- create worktree -----------------------------------------------------
wt_path="$SESSION_ROOT/$branch"
if [ -e "$wt_path" ]; then
  warn "Removing stale path: $wt_path"
  rm -rf "$wt_path"
fi

bold "Branch:   $branch"
bold "Worktree: $wt_path"
git worktree add -b "$branch" "$wt_path" "origin/$SESSION_BASE" \
  || { err "git worktree add failed"; exit 1; }

echo ""
ok "Session ready."
echo "  1. cd $wt_path"
echo "  2. do the work; commit on '$branch'"
echo "  3. open a PR into $SESSION_BASE"
