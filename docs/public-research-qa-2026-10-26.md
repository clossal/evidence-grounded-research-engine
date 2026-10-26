# Public Research Engine QA — 2026-10-26

## Scope and isolation

This review exercised the separate public-research API and UI at
`/public-research`. It uses only the five allow-listed, licensed public reports
in the local public-demo workspace (850 original PDF pages; 3,080 indexed
chunks). Its OpenAPI surface contains only public-research routes; it has no
Economist, private-session, or private-memory route. The public engine does not
import the private Economist retrieval or memory services.

The PDFs and generated local public index remain excluded from source control.
The tracked manifest preserves publisher URL, licence information, page count,
and SHA-256 provenance without distributing source text.

## Functional checks

| Check | Result | Evidence |
| --- | --- | --- |
| Public health, document listing, question, observation and revision routes | PASS | Live API check; malformed question received HTTP 422. |
| Frontend → FastAPI → MiniLM/FAISS → local Qwen → citation card | PASS | Browser question about the UK AI Playbook returned the supported ten-principle answer with a page-9 citation. |
| Publisher citation link | PASS | Browser citation expands to the publisher PDF URL with `#page=9`. |
| Observation review, immutable revision and detail controls | PASS | Browser exposes detail, evidence-supported review, revision, history and lineage controls. |
| Observation persistence | PASS | The reviewed/revised records remained after a clean public-backend restart. |
| Reviewed-memory advisory mode | PASS (mechanism) | API response recorded selected reviewed observation IDs; prompt labels memory as advisory and still requires fresh evidence citations. This is not evidence that memory improves answer quality. |
| Private/public isolation | PASS | Public OpenAPI inventory contains no private routes; regression coverage rejects private-service imports. |
| Browser errors | PASS | No console errors during cited-answer, citation-detail and memory-detail checks. |
| Backend tests | PASS | 41 passed. |
| TypeScript and production build | PASS | `npx tsc --noEmit` and `npm run build` passed. |

The local npm CLI emits a compatibility warning for npm 12.2.0 with Node 20.20.2,
but the application type check and production build completed successfully. Pin a
supported npm/Node pair before a hosted release.

## Source-grounded answer checks

Answers were produced through the real local pipeline, then checked against the
named original PDF pages. A valid citation marker alone was not considered a
pass.

| Case | Outcome | Classification |
| --- | --- | --- |
| UK AI Playbook: number of common principles | PASS | Direct fact; answer gave ten and linked to p. 9. |
| Advanced-AI safety: limitation of technical safety methods | PASS | Qualified claim cited p. 68, which supports the limitation. |
| AI-safety report vs. AI Playbook: mitigation and accountability | PASS | Cross-document response cited both reports and separated their roles. |
| World Development Report: 1i/2i/3i development strategy | PASS, limited | Correct high-level structure with supporting cited pages; retain a manual editorial check before using in a recorded demo. |
| Strategic Competition report: methodology | FAIL | Retrieval/ranking selected pages about interactions and study timing rather than the reviewed methodology pages. The system did not invent a method, but it did not answer the question. |
| Public Health England report: role in policy and practice | FAIL | Safe abstention despite relevant material in the PDF: a retrieval/selection coverage failure. |
| PHE 2026 inflation forecast | PASS | Correct insufficient-evidence abstention with no citations. |
| Current global AI-safety regulation | PASS | Correct live-information abstention with no citations. |

This is **not** a generalization benchmark. It is a release QA sample. The two
retrieval/selection failures mean the product must not promise complete coverage
of every question in an indexed report. The UI clearly returns insufficiency
instead of fabricating an answer for the PHE case; the methodology case remains
an open answer-quality limitation.

## Fixes included in this QA pass

- Made public-document publisher URLs available in cited evidence and rendered
  them as page-deep links in the UI.
- Added an opt-in, advisory-only reviewed-memory path. Fresh retrieved evidence
  and citations remain mandatory for every factual answer.
- Added reviewable observation details, status, provenance, history, revision
  lineage and immutable revision creation in the public UI/API.
- Hardened answer validation so citation-only output and an embedded
  `INSUFFICIENT_EVIDENCE` string cannot be reported as an answered result.
- Narrowed the temporal guard so historical terms such as “current account in
  2022” remain answerable while requests for live facts abstain.

## Release decision

**Conditional NO-GO for an unconditional accuracy claim; GO for a clearly
limited local portfolio release.** The application is functionally launchable,
isolated from private Economist data, and has verified successful cited-answer
paths. Its README/demo must disclose that local retrieval can miss relevant
material and that reviewed memory is advisory rather than learned knowledge.
Only use the four passing demonstration questions above after a final manual
source-page check; do not use the two failed answerable cases in a walkthrough.

