"""Regression coverage for the isolated public research surface."""

from backend.public_research_demo import PublicResearchDemo


def test_temporal_guard_allows_historical_current_account_questions():
    assert not PublicResearchDemo._requires_live_information(
        "What was the current account deficit in 2022?"
    )


def test_temporal_guard_blocks_live_questions():
    assert PublicResearchDemo._requires_live_information(
        "What is the current global AI safety regulation?"
    )


def test_answer_validation_rejects_marker_only_and_embedded_abstention():
    allowed = {"P1"}
    assert not PublicResearchDemo._valid_answer("- [P1]", allowed)
    assert not PublicResearchDemo._valid_answer(
        "- INSUFFICIENT_EVIDENCE [P1]", allowed
    )
    assert not PublicResearchDemo._valid_answer(
        "- Insufficient evidence for a detailed answer. [P1]", allowed
    )
    assert PublicResearchDemo._valid_answer(
        "- The report identifies ten common principles. [P1]", allowed
    )


def test_public_module_does_not_import_private_economist_services():
    source = open("backend/public_research_demo.py", encoding="utf-8").read()
    prohibited = ("economist_index", "ollama_rag", "research_memory.sqlite")
    assert all(token not in source for token in prohibited)
