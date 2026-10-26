"""Independent public-research API. It intentionally has no private routes."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .public_research_demo import PublicResearchDemo

app = FastAPI(title="Document Intelligence — Public Research Demo", version="1")
app.add_middleware(CORSMiddleware, allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+", allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
ENGINE: PublicResearchDemo | None = None


def engine() -> PublicResearchDemo:
    global ENGINE
    if ENGINE is None:
        ENGINE = PublicResearchDemo()
    return ENGINE


class Ask(BaseModel):
    question: str = Field(min_length=1, max_length=2_000)
    document_ids: list[str] = Field(min_length=1, max_length=8)
    use_memory: bool = False


class Observation(BaseModel):
    statement: str = Field(min_length=1, max_length=2_000)
    evidence_ids: list[str] = Field(min_length=1, max_length=8)
    confidence: float = Field(default=0.5, ge=0, le=1)


class Revision(BaseModel):
    statement: str = Field(min_length=1, max_length=2_000)
    rationale: str = Field(min_length=1, max_length=2_000)


@app.get("/api/v1/health")
def health() -> dict[str, object]:
    return {"ok": True, "mode": "public-research-demo", "private_corpus_access": False}


@app.post("/api/v1/public-research/ingest")
def ingest() -> dict[str, object]:
    try:
        return engine().ingest_directory()
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc


@app.get("/api/v1/public-research/documents")
def documents() -> list[dict[str, object]]:
    return engine().documents()


@app.post("/api/v1/public-research/ask")
def ask(request: Ask) -> dict[str, object]:
    try:
        return engine().ask(request.question.strip(), request.document_ids, request.use_memory)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc


@app.get("/api/v1/public-research/observations")
def observations() -> list[dict[str, object]]:
    return engine().observations()


@app.get("/api/v1/public-research/observations/{observation_id}")
def observation(observation_id: str) -> dict[str, object]:
    try:
        return engine().observation(observation_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.post("/api/v1/public-research/runs/{run_id}/observations")
def save_observation(run_id: str, observation: Observation) -> dict[str, object]:
    try:
        return engine().save_observation(run_id, observation.statement, observation.evidence_ids, observation.confidence)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.post("/api/v1/public-research/observations/{observation_id}/review/{status}")
def review_observation(observation_id: str, status: str) -> dict[str, object]:
    try:
        return engine().review_observation(observation_id, status)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.post("/api/v1/public-research/observations/{observation_id}/revise")
def revise_observation(observation_id: str, revision: Revision) -> dict[str, object]:
    try:
        return engine().revise_observation(observation_id, revision.statement, revision.rationale)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
