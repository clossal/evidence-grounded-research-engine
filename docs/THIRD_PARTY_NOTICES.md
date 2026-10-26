# Third-party and model notices

## Project license

The source code and synthetic fixtures in this repository are offered under
the MIT License in `LICENSE`. That license applies only to the original work
in this repository; it does not relicense dependencies, downloaded models,
user uploads, or documents processed with the application.

## Runtime dependencies

The direct frontend dependencies declared in `frontend/package.json` are MIT,
ISC, or Apache-2.0 licensed. The direct Python dependencies are permissively
licensed (including FastAPI under MIT, Uvicorn under BSD-3-Clause,
pdfplumber under MIT, NumPy under BSD-3-Clause, and Sentence Transformers under
Apache-2.0). Their transitive dependencies retain their own terms. Package
managers install their license notices with their distributions; downstream
redistributors should generate a complete dependency notice/SBOM for their
target platform and versions.

## Local model and external runtime

The repository contains no model weights, Ollama runtime, or embedding-model
files. Users obtain those separately and must review the license, model card,
acceptable-use policy, and redistribution terms at the selected source.

The documented Qwen2.5-7B-Instruct model card identifies Apache-2.0, but this
repository does **not** redistribute it or grant rights in it. Likewise,
installing Ollama or PyTorch is an end-user action governed by their own terms.

## Documents and generated results

Only independently authored synthetic PDFs are included. Do not add customer
uploads, publisher content, private indexes, extracted passages, embeddings,
or generated results derived from documents you do not have permission to
redistribute.

## Review sources

- Next.js: MIT — <https://github.com/vercel/next.js>
- pdfplumber: MIT — <https://github.com/jsvine/pdfplumber>
- Sentence Transformers: Apache-2.0 — <https://github.com/huggingface/sentence-transformers>
- PyTorch: BSD-style — <https://github.com/pytorch/pytorch>
- Qwen2.5-7B-Instruct model card: Apache-2.0 — <https://huggingface.co/Qwen/Qwen2.5-7B-Instruct>

This notice is an engineering inventory, not legal advice.
