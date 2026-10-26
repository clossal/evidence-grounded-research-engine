# Public Research Engine

Local, evidence-grounded research over a small collection of documents that you
are permitted to process. It provides page-level citations, a reviewable
observation ledger, and optional advisory memory. It runs locally and does not
send documents or prompts to a paid API.

## What is (and is not) included

This release includes code, synthetic test PDFs, and a provenance manifest for
the optional public research-demo collection. It does **not** include publisher
PDFs, extracted text, vector indexes, local model weights, customer documents,
or private research data. Download documents only from their publishers and
respect their licences and third-party-material restrictions.

## Requirements

- Python 3.11+
- Node.js 20+ and a supported npm version
- A local Ollama-compatible service with a Qwen-class instruction model
- About 4 GB RAM for the embedding model plus the memory required by your local
  generation model

## Quick start

```bash
python -m venv .venv
.venv/bin/pip install -r backend/requirements.txt

# Put your own permitted text PDFs in data/public-research-demo/pdfs/.
# Record provenance and licence details in data/public-research-demo/manifest.json.
export OLLAMA_MODEL=qwen2.5:7b
export MINILM_PATH=/absolute/path/to/all-MiniLM-L6-v2
.venv/bin/python scripts/index_public_research_demo.py

.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8003
```

In a second terminal:

```bash
cd frontend
npm ci
NEXT_PUBLIC_PUBLIC_RESEARCH_URL=http://127.0.0.1:8003 npm run dev
```

Open `http://127.0.0.1:3000`.

## Safety model

- Answers must cite fresh retrieved evidence. If evidence is absent, the system
  returns an insufficient-evidence result.
- Saved observations start as candidates. Reviews and revisions are retained as
  history; memory is advisory and never replaces source citations.
- The local runtime database and index live under
  `data/public-research-demo/runtime/` and are ignored by Git.

## Known limitations

Local semantic retrieval can miss relevant pages in long reports. Treat answers
as research assistance, inspect the cited source page, and do not treat memory
as verified truth. The application is a single-user local demo, not a
multi-tenant service.

## Release checks

Run `scripts/audit-public-release.sh` from a fresh exported repository after
initialising its new Git history. See `docs/public-research-qa-2026-10-26.md`
for the source-grounded QA sample and `docs/public-research-screenshot-checklist.md`
for safe portfolio screenshots.

