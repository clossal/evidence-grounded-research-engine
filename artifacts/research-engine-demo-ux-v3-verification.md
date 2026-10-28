# Research Workspace UX Video Verification — 2026-10-28

## Result

- Final file: `artifacts/research-engine-demo-ux-v3-short.mp4`
- Runtime: 45.04 seconds; H.264 video, AAC audio, 1920×1080.
- Source recording: `artifacts/raw-video-ux/research-engine-demo-ux-1793166814802.webm`.
- Timeline: `artifacts/research-engine-demo-ux-v2-events.jsonl`.
- Edit decisions: `artifacts/research-engine-demo-ux-v3-short-edits.json`.

## Visible, real interactions

1. The public Research Workspace opens with the question field above the fold.
2. The Playbook question is typed through Playwright's sequential key events,
   submitted through the actual button, and answered by the local service with
   a page-level citation.
3. The evidence disclosure and publisher-page link are opened in the viewport.
4. A two-document comparison is submitted and its evidence-grounded response
   is shown, followed by a reviewed observation and its provenance.
5. An out-of-corpus inflation question returns the UI's explicit
   `Insufficient evidence` state.

The event ledger records HTTP 200 answers for the single-document and
cross-document requests and an HTTP 200 `insufficient_evidence` result for the
negative control. The only console event recorded was a missing favicon (404);
there were no page exceptions.

## Editing and visual review

The source browser recording is preserved. The edit worker retains real typing,
submission, answer rendering, citation inspection, memory interaction, and
abstention frames. It removes inference waits and labels the retained
one-second processing cues as `Inference wait shortened`.

Frames at edit boundaries and sampled timeline points are retained in
`artifacts/edit-checks-ux-v3/` and `artifacts/ux-video-checks-v3/`. Black-frame
detection reported no black intervals. Static-frame detection reported only
intentional readable answer/citation holds.

## Privacy

The recording uses only the isolated public research collection. It contains no
Economist files, private index paths, or private-session content. The
source-only release audit passed after recording.
