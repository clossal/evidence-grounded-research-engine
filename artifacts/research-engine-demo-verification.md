# Research Engine video verification

## Artifact integrity

- Final MP4: `artifacts/research-engine-demo.mp4`
- Raw browser capture retained: `artifacts/raw-video/research-engine-demo.webm`
- Duration: **185.56 seconds** (03:05.56)
- Video: H.264, 1920 x 1080, 25 fps
- Audio: AAC silent compatibility track, 48 kHz stereo
- Event ledger: `artifacts/research-engine-demo-events.jsonl`
- Checkpoint screenshots: `artifacts/screenshots/`

The raw recording was captured by Playwright from the running local frontend.
The MP4 is a direct transcode of that raw capture with no scene replacement,
answer substitution, or speed-up. A prior failed recorder attempt is retained
separately under `artifacts/raw-video/` and was not used in the final export.

## Real request verification

The final event ledger records four actual `POST` answer interactions against
the local public backend. The frontend was observed to render each final state
before the recorder continued.

| Scenario | Backend run ID | Backend result | Evidence | Visible validation |
| --- | --- | --- | --- | --- |
| UK AI Playbook — ten principles | `run_a6446591fb554adb84f3a4b0b2df0b1a` | `answered` | 1 item | Answer, `[P1]`, evidence title, and page-9 publisher link shown. |
| AI Safety Report — technical-method limitation | `run_83be3239c6034b4dbe9d402a2a6df8bf` | `answered` | 1 item | Answer and evidence panel show page 68. |
| Cross-document mitigation/accountability comparison | `run_f1fbbec2582f4c83b0e3b448b8321ef3` | `answered` | 5 items | Selected documents, answer markers, and evidence panel shown. `memory_used` was 2, and the UI labels memory as advisory. |
| Unsupported PHE inflation forecast | `run_af82fe712c8e4c308174ec6ab3c0ab9a` | `insufficient_evidence` | 0 items | Explicit abstention shown; no citation is fabricated. |

The recorder waited for both the HTTP response and the rendered UI state. It
also checked the selected question value, citation visibility for answerable
requests, and visible answer/abstention text. It scrolled the recorded viewport
before holding on evidence and memory sections.

## Citation checks

- **UK AI Playbook:** the visible citation is the official UK publisher PDF URL
  targeting page 9; the answer reports ten principles.
- **AI Safety Report:** the visible evidence record identifies the International
  Scientific Report on the Safety of Advanced AI, page 68, for the stated
  limitation.
- **Cross-document response:** citations are displayed as fresh evidence markers
  rather than memory markers. The selected documents are the Playbook and the
  Safety Report.
- **Abstention:** the application returns no evidence item and makes no
  numerical claim.

## Privacy and source boundary check

The capture used the isolated public-demo configuration and did not access the
private Economist corpus, its index, its sessions, or its observations. No
private paths, credentials, PDF pages, or third-party figures are visible in
the sampled frames. The video only shows the application interface, source
metadata, brief evidence excerpts, and publisher links for the public reports.

## Visual review

Frames sampled at 00:08, 00:35, 01:15, 02:00, 02:45, and 03:01 show distinct
workflow stages. They confirm a readable library, single-document answers,
citation details, cross-document answer, and final abstention. No blank screen
or truncated ending was observed. The 404 noted in the final recorder ledger is
an incidental browser resource request; it did not affect any answer request
or the visible interface.

## Limitation

This recording demonstrates a local, single-user workflow. It does not claim
that reviewed memory is independently verified truth, that it improves model
reasoning, or that the application is a multi-tenant hosted service.
