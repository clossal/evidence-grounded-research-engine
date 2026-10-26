"""Local model settings shared by the standalone document demo.

This module deliberately has no dependency on the private archive RAG stack,
so the PDF-first application can be released and run on its own.
"""
from __future__ import annotations

import os
import re
from pathlib import Path


MINILM_PATH = Path(os.environ.get("MINILM_PATH", str(Path(__file__).resolve().parents[1] / "models" / "minilm")))
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
OLLAMA_TIMEOUT = float(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "180"))


def temporal_scope(question: str) -> str:
    """Classify only the temporal intent needed for document-only answers."""
    text = re.sub(r"\s+", " ", question.lower()).strip()
    if re.search(r"\b(?:19|20)\d{2}\b", text) or re.search(
            r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b", text):
        return "historical"
    live_terms = r"current|today|latest|live|right now|at present|currently|this week|this month"
    # "Current account" names a measure; it does not by itself request a live fact.
    without_account = re.sub(r"\bcurrent account\b", "", text)
    if re.search(rf"\b(?:{live_terms})\b", without_account):
        return "live"
    return "unspecified"
