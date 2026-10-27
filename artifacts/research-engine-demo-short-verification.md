# Short research-engine highlight verification

## Output

- Video: `artifacts/research-engine-demo-short.mp4`
- Duration: **54.44 seconds** (maximum allowed: 60 seconds)
- Format: H.264, 1920 x 1080, 25 fps, AAC silent compatibility track
- Source video preserved unchanged: `artifacts/research-engine-demo.mp4`
- Source SHA-256: `15bd4d305a6159f122ddb8718a0d57b13fc1022e1a7fcdb6e23bd4bb05cc1368`
- Highlight SHA-256: `f8084c7dbed49a44fa492cf284d468033716b4849f39dc5fa4b5366e3837a9e5`
- Edit log: `artifacts/research-engine-demo-short-edits.json`
- Boundary-frame review packet: `artifacts/edit-checks/`

## Editorial decisions

The event-aware worker aligned the source MP4 to the browser event ledger with
a **-0.077-second** difference across the full recording. It selected eight
real source intervals:

1. Public workspace introduction (4.00 s).
2. UK AI Playbook question and cited answer (9.44 s).
3. Citation metadata and publisher page-9 link (5.20 s).
4. Cross-document question submission (1.80 s).
5. A real one-second researching state, captioned **“Inference wait shortened”**.
6. Cross-document answer with fresh source markers (11.65 s).
7. Reviewed-memory observation detail (10.10 s).
8. Unsupported-question abstention (11.14 s).

Long inference intervals were removed rather than sped through. Every shown
answer is preceded by its own visible question; no answer, citation, or memory
record has been transplanted from another request.

## Automated and visual checks

- FFmpeg fully decoded the final MP4 without errors.
- `ffprobe` confirms one H.264 video stream, one AAC stream, and a 54.44-second
  container duration.
- `blackdetect` found no black interval of 0.5 seconds or longer.
- The worker extracted frames immediately before and after every edit boundary.
  Manual inspection confirmed visible progression through the workspace,
  single-document answer, citation, researching state, cross-document answer,
  observation detail, and abstention.
- `freezedetect` reports short 2.1–3.5 second static periods. They occur during
  deliberate readable holds on answers, citations, or the observation card—not
  during retained inference waiting. No long waiting screen remains.
- The edit log retains each source interval, question identifier, caption, and
  reason, making the edit reproducible and auditable.

## Authenticity and privacy

The video consists solely of direct extracts from the real browser recording.
The only overlay is the wait-shortening disclosure. It uses the isolated public
research configuration; no private Economist documents, indexes, paths,
sessions, observations, credentials, PDF pages, or third-party figures appear.

## Limitation

The short format demonstrates persistence/review of advisory memory but does
not claim that memory improves model reasoning. It is a local single-user demo,
not evidence of a hosted or multi-tenant deployment.
