#!/usr/bin/env python3
"""Build or resume only the isolated public-demo corpus index."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.public_research_demo import PublicResearchDemo

if __name__ == "__main__":
    print(json.dumps(PublicResearchDemo().ingest_directory(), indent=2))
