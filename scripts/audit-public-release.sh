#!/usr/bin/env bash
# Audit an allow-listed public export. Run from the export root after `git init`.
set -euo pipefail

if [[ ! -f README.md || ! -d .git ]]; then
  echo "Run this script from an initialized public-release repository." >&2
  exit 2
fi

fail=0
check_absent() {
  local label=$1
  shift
  local matches
  matches=$(find . -path './.git' -prune -o "$@" -print)
  if [[ -n $matches ]]; then
    echo "FAIL: $label" >&2
    printf '%s\n' "$matches" >&2
    fail=1
  fi
}

check_absent "private/runtime artifacts present" \
  \( -iname '*.gguf' -o -iname '*.sqlite' -o -iname '*.db' -o -iname '*.faiss' -o -iname '*.index' -o -iname '*.npy' \)
check_absent "environment file present" \( -name '.env' -o -name '.env.local' -o -name '.env.production' \)

pdfs=$(find . -path './.git' -prune -o -type f -iname '*.pdf' -print)
if [[ -n $pdfs ]] && printf '%s\n' "$pdfs" | grep -qv '^./backend/tests/fixtures/'; then
  echo "FAIL: PDF outside synthetic fixture directory" >&2
  printf '%s\n' "$pdfs" | grep -v '^./backend/tests/fixtures/' >&2
  fail=1
fi

if rg -n -i --hidden --glob '!.git/**' --glob '!scripts/audit-public-release.sh' \
  --glob '!frontend/.next*/**' --glob '!frontend/node_modules/**' --glob '!**/__pycache__/**' \
  '(the economist|economist-rag|/run/media/|/mnt/data/)' .; then
  echo "FAIL: private corpus or path reference found" >&2
  fail=1
fi

if rg -n -i --hidden --glob '!.git/**' --glob '!scripts/audit-public-release.sh' \
  --glob '!frontend/.next*/**' --glob '!frontend/node_modules/**' --glob '!**/__pycache__/**' \
  '(sk-[A-Za-z0-9_-]{16,}|hf_[A-Za-z0-9]{16,}|authorization:[[:space:]]*bearer)' .; then
  echo "FAIL: credential-shaped value found" >&2
  fail=1
fi

echo "--- tracked public files ---"
git ls-files | sort
echo "--- fresh history ---"
git log --all --oneline --decorate
echo "--- synthetic fixture hashes ---"
if [[ -d backend/tests/fixtures ]]; then
  find backend/tests/fixtures -type f -iname '*.pdf' -print0 | sort -z | xargs -0 -r sha256sum
fi

if (( fail )); then
  exit 1
fi
echo "PASS: no prohibited runtime artifacts, non-fixture PDFs, private corpus paths, or credential-shaped values found."
