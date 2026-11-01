"""Load and validate the bundled synthetic debugging cases."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "synthetic_cases.json"

def load_cases(path: str | Path = DATA_PATH) -> list[dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as handle:
        cases = json.load(handle)
    if not isinstance(cases, list) or not cases:
        raise ValueError("Dataset must be a non-empty JSON array.")
    required = {"case_id", "title", "logs", "expected_root_cause"}
    for index, case in enumerate(cases):
        missing = required - case.keys()
        if missing:
            raise ValueError(f"Case {index} is missing fields: {sorted(missing)}")
    return cases
