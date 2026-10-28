# Research Workspace UX and recording QA — 2026-10-27

Scope: isolated public release candidate only. The private Economist project,
index, and data stores were not opened or changed.

## Verified browser workflow

- At a 1920×1080 viewport, the `Your research question` textarea and actual
  `Ask with cited evidence` control are visible in the initial workspace
  viewport.
- The separate `/library` route lists the public documents; a selection made
  there persists in browser local storage after returning to `/`.
- A real Qwen request answered the UK AI Playbook question: **10 common
  principles**, with `P1` resolving to the Playbook, page 9.
- The recorded cross-document request used the AI Safety Report and the UK AI
  Playbook, rendered an evidence-grounded answer, and displayed evidence.
- The recording opened a reviewed-memory card and finished with the intended
  out-of-corpus abstention.

## Recording authenticity checks

- Source: `artifacts/raw-video-ux/research-engine-demo-ux-1793117760420.webm`
- Edited output: `artifacts/research-engine-demo-ux-short.mp4` (55.12 seconds,
  1920×1080 H.264/AAC).
- Timeline: `artifacts/research-engine-demo-ux-events.jsonl`; it records
  sequential typing, submission, backend response, frontend render, wheel
  scrolling, citation expansion, memory detail, and abstention.
- Frame samples at 2, 10, 20, 31, 42, and 48 seconds are under
  `artifacts/ux-video-checks/`. They show the workspace, cited answer,
  real processing state, cross-document flow, and completed final state.
- No black-frame events were found. The only browser-console entry was a
  non-blocking missing development asset (HTTP 404); no application exception
  was observed in the recorded workflow.

## Limits

The demo is local and single-user. Qwen latency varies by host; the event-aware
edit retains a real processing cue and labels the removed remainder as
"Inference wait shortened". Publisher PDFs,
private corpora, model weights, and indexes are not part of the public source
release.
