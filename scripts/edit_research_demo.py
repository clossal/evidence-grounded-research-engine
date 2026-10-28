#!/usr/bin/env python3
"""Create a short, evidence-preserving highlight from a recorded demo session.

The worker intentionally uses the browser's JSONL event ledger as its editing
source of truth. It never manufactures an answer or substitutes screenshots:
every output interval is copied from the recorded browser video.  It retains a
brief processing cue before long inference waits and labels that compression.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO = ROOT / "artifacts/research-engine-demo.mp4"
DEFAULT_EVENTS = ROOT / "artifacts/research-engine-demo-events.jsonl"
DEFAULT_OUTPUT = ROOT / "artifacts/research-engine-demo-short.mp4"
DEFAULT_LOG = ROOT / "artifacts/research-engine-demo-short-edits.json"
CHECKS = ROOT / "artifacts/edit-checks"


@dataclass
class Segment:
    name: str
    start: float
    end: float
    reason: str
    question_id: str | None = None
    speed: float = 1.0
    caption: str | None = None

    @property
    def duration(self) -> float:
        return max(0.0, (self.end - self.start) / self.speed)


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, capture_output=capture)


def ffprobe(path: Path) -> dict[str, Any]:
    result = run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration,size",
        "-show_entries", "stream=codec_name,width,height,avg_frame_rate",
        "-of", "json", str(path),
    ], capture=True)
    return json.loads(result.stdout)


def read_events(path: Path) -> list[dict[str, Any]]:
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not records or records[0].get("event") != "recording_started":
        raise ValueError("Event ledger must begin with recording_started.")
    base = datetime.fromisoformat(records[0]["timestamp"].replace("Z", "+00:00"))
    for record in records:
        stamp = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
        record["video_time"] = round((stamp - base).total_seconds(), 3)
    return records


def first(records: list[dict[str, Any]], event: str, **match: Any) -> dict[str, Any]:
    for record in records:
        if record.get("event") == event and all(record.get(key) == value for key, value in match.items()):
            return record
    raise ValueError(f"Missing event {event} matching {match}.")


def event_duration(records: list[dict[str, Any]]) -> float:
    return float(records[-1]["video_time"])


def bounded(start: float, end: float, duration: float) -> tuple[float, float]:
    start = max(0.0, start)
    end = min(duration, end)
    if end <= start:
        raise ValueError(f"Invalid source range {start}–{end}.")
    return round(start, 3), round(end, 3)


def choose_storyboard(records: list[dict[str, Any]], duration: float) -> list[Segment]:
    """Build a concise story from generic lifecycle events, not source text."""
    questions = [record for record in records if record.get("event") == "question_entered"]
    answers = [record for record in records if record.get("event") == "frontend_answer_rendered"]
    answered_ids = [record["id"] for record in answers if record.get("result_status") == "answered"]
    if not answered_ids:
        raise ValueError("No completed grounded answer is available for a highlight.")

    # The first answered request establishes question → answer → citation. The
    # completed answer with most evidence demonstrates cross-document research.
    first_id = answered_ids[0]
    response_records = [record for record in records if record.get("event") == "backend_response"]
    cross_response = max(
        (record for record in response_records if record.get("result_status") == "answered"),
        key=lambda record: (record.get("evidence_count", 0), record.get("memory_used", 0)),
    )
    cross_id = cross_response["id"]
    abstention = next((record for record in answers if record.get("result_status") == "insufficient_evidence"), None)

    first_question = first(records, "question_entered", id=first_id)
    first_render = first(records, "frontend_answer_rendered", id=first_id)
    citation = first(records, "citation_opened", question=first_id)
    cross_question = first(records, "question_entered", id=cross_id)
    cross_render = first(records, "frontend_answer_rendered", id=cross_id)
    memory = first(records, "memory_detail_opened")
    first_event = first(records, "library_rendered")

    segments: list[Segment] = []
    start, end = bounded(first_event["video_time"], first_event["video_time"] + 3.0, duration)
    segments.append(Segment("workspace-introduction", start, end, "Show isolated public research workspace."))

    # Preserve the visible character-by-character typing and a short genuine
    # researching state, then cut to the actual rendered answer. Long local
    # inference waits add no viewing value and are explicitly labelled.
    start, end = bounded(first_question["video_time"] - 3.6, first_question["video_time"] + 0.3, duration)
    segments.append(Segment("single-document-question-typing", start, end, "Show the real typed research question and submission.", first_id))
    start, end = bounded(first_question["video_time"] + 0.3, first_question["video_time"] + 1.3, duration)
    segments.append(Segment("single-document-processing-cue", start, end, "Retain a real processing cue; omit remaining inference wait.", first_id, caption="Inference wait shortened"))
    start, end = bounded(first_render["video_time"] - 0.15, first_render["video_time"] + 7.0, duration)
    segments.append(Segment("single-document-answer", start, end, "Show the real grounded answer at readable speed.", first_id))
    start, end = bounded(citation["video_time"] - 0.2, citation["video_time"] + 4.0, duration)
    segments.append(Segment("citation-inspection", start, end, "Show citation metadata and publisher page link.", first_id))

    # Keep a genuine one-second researching state, but remove the remainder of
    # the inference wait. The caption makes that compression explicit.
    cue_start, cue_end = bounded(cross_question["video_time"] - 0.7, cross_question["video_time"] + 1.1, duration)
    segments.append(Segment("cross-document-submission", cue_start, cue_end, "Show two-document question submission.", cross_id))
    wait_start, wait_end = bounded(cross_question["video_time"] + 1.1, cross_question["video_time"] + 2.1, duration)
    segments.append(Segment("cross-document-processing-cue", wait_start, wait_end, "Retain a real processing cue; omit remaining inference wait.", cross_id, caption="Inference wait shortened"))
    start, end = bounded(cross_render["video_time"] - 0.15, cross_render["video_time"] + 8.0, duration)
    segments.append(Segment("cross-document-answer", start, end, "Show multi-source answer and fresh citations.", cross_id))

    start, end = bounded(memory["video_time"] - 0.6, memory["video_time"] + 6.0, duration)
    segments.append(Segment("reviewed-memory", start, end, "Show observation detail and provenance state."))

    if abstention:
        abstention_question = first(records, "question_entered", id=abstention["id"])
        start, end = bounded(abstention_question["video_time"] - 0.5, abstention["video_time"] + 6.0, duration)
        segments.append(Segment("responsible-abstention", start, end, "Show unsupported question and explicit abstention.", abstention["id"]))

    return segments


def extract_segment(source: Path, destination: Path, segment: Segment, font: Path | None) -> None:
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{segment.start:.3f}", "-to", f"{segment.end:.3f}", "-i", str(source),
        "-an",
    ]
    video_filter = []
    if segment.speed != 1.0:
        video_filter.append(f"setpts=PTS/{segment.speed}")
    if segment.caption:
        if not font:
            raise RuntimeError("No usable font found for compression caption.")
        escaped = segment.caption.replace("'", r"\\'").replace(":", r"\\:")
        video_filter.append(
            "drawtext="
            f"fontfile={font}:text='{escaped}':fontcolor=white:fontsize=34:"
            "x=(w-text_w)/2:y=h-110:box=1:boxcolor=black@0.60:boxborderw=18"
        )
    if video_filter:
        command += ["-vf", ",".join(video_filter)]
    command += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", str(destination)]
    run(command)


def sample_frame(video: Path, timestamp: float, destination: Path) -> None:
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{timestamp:.3f}",
        "-i", str(video), "-frames:v", "1", "-update", "1", str(destination),
    ])


def detect_black(video: Path) -> list[str]:
    completed = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(video), "-vf", "blackdetect=d=0.50:pix_th=0.08", "-an", "-f", "null", "-"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    return [line.strip() for line in completed.stderr.splitlines() if "black_start" in line]


def detect_freezes(video: Path) -> list[str]:
    """Report visually static runs for editorial review, not as automatic cuts.

    A grounded answer can be intentionally static while it remains on screen
    long enough to read.  These findings are therefore logged for human review
    instead of treating all static UI as an error.
    """
    completed = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(video), "-vf", "freezedetect=n=0.001:d=2", "-an", "-f", "null", "-"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    return [line.strip() for line in completed.stderr.splitlines() if "freezedetect.freeze_" in line]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--edits", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--max-duration", type=float, default=60.0)
    parser.add_argument("--checks", type=Path, default=CHECKS, help="Directory for visual-review frames.")
    args = parser.parse_args()

    if not args.input.is_file() or not args.events.is_file():
        raise SystemExit("Input MP4 and JSONL event ledger must both exist.")
    source_probe = ffprobe(args.input)
    source_duration = float(source_probe["format"]["duration"])
    events = read_events(args.events)
    ledger_duration = event_duration(events)
    alignment_delta = round(source_duration - ledger_duration, 3)
    # Browser video files commonly contain a short tail while Playwright closes
    # the context. Event timestamps still begin with the first rendered frame,
    # so a source-only tail is safe to trim. Other drift needs manual review.
    if alignment_delta < -3.0 or alignment_delta > 6.0:
        raise SystemExit(
            f"Event/video timing differs by {alignment_delta}s; inspect source footage before cutting."
        )

    storyboard = choose_storyboard(events, source_duration)
    planned_duration = round(sum(segment.duration for segment in storyboard), 3)
    if planned_duration > args.max_duration:
        raise SystemExit(f"Planned duration {planned_duration}s exceeds {args.max_duration}s.")

    font_candidates = [
        Path("/usr/share/fonts/noto/NotoSans-Regular.ttf"),
        Path("/usr/share/fonts/TTF/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    font = next((candidate for candidate in font_candidates if candidate.is_file()), None)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.edits.parent.mkdir(parents=True, exist_ok=True)
    checks = args.checks.resolve()
    checks.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="research-demo-edit-") as temporary:
        work = Path(temporary)
        parts: list[Path] = []
        for index, segment in enumerate(storyboard):
            part = work / f"part-{index:02d}.mp4"
            extract_segment(args.input, part, segment, font)
            parts.append(part)
        concat_file = work / "concat.txt"
        concat_file.write_text("".join(f"file '{part}'\n" for part in parts))
        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_file), "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(args.output),
        ])

    output_probe = ffprobe(args.output)
    output_duration = float(output_probe["format"]["duration"])
    if output_duration > args.max_duration + 0.05:
        raise SystemExit(f"Rendered output {output_duration}s exceeds allowed maximum.")

    # Capture frames immediately before/after each edit boundary. They provide a
    # durable visual review packet and prevent relying on DOM/API success alone.
    offset = 0.0
    frame_checks = []
    for index, segment in enumerate(storyboard):
        for point, label in ((max(0.05, offset + 0.15), "start"), (max(0.05, offset + segment.duration - 0.15), "end")):
            frame = checks / f"short-{index:02d}-{segment.name}-{label}.png"
            sample_frame(args.output, point, frame)
            frame_checks.append({"segment": segment.name, "point": label, "output_time": round(point, 3), "frame": str(frame.relative_to(ROOT))})
        offset += segment.duration

    black = detect_black(args.output)
    freezes = detect_freezes(args.output)
    decision_log = {
        "schema": "research-engine-demo-edit-log/v1",
        "source_video": str(args.input.relative_to(ROOT)),
        "event_timeline": str(args.events.relative_to(ROOT)),
        "source_duration_seconds": source_duration,
        "event_span_seconds": ledger_duration,
        "alignment_delta_seconds": alignment_delta,
        "alignment_note": "A positive delta up to six seconds is a confirmed Playwright shutdown tail; source intervals remain anchored to the recording-start event.",
        "output_video": str(args.output.relative_to(ROOT)),
        "output_duration_seconds": output_duration,
        "max_duration_seconds": args.max_duration,
        "segments": [asdict(segment) | {"output_duration": round(segment.duration, 3)} for segment in storyboard],
        "frame_checks": frame_checks,
        "black_detect_events": black,
        "static_ui_review_events": freezes,
        "static_ui_review_note": "Static runs are expected only during readable answer, citation, or memory holds; processing waits are limited to the labeled one-second cue.",
        "authenticity": "Every content segment is directly extracted from the source recording; only the wait-compression caption is overlaid.",
    }
    args.edits.write_text(json.dumps(decision_log, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "duration": output_duration, "segments": len(storyboard)}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, subprocess.CalledProcessError, RuntimeError) as error:
        print(f"edit worker failed safely: {error}", file=sys.stderr)
        raise SystemExit(1)
