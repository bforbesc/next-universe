"""Loads the baseline curriculum. The generator personalizes *this* content —
it never invents the course."""
import json
from functools import lru_cache

from ..config import CURRICULUM_PATH

VERTICAL_SLICE = ["variables", "conditionals", "loops"]


@lru_cache(maxsize=1)
def load_curriculum() -> dict:
    with open(CURRICULUM_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_modules(concepts: list[str] | None = None) -> list[dict]:
    """Return curriculum modules for the requested concepts, in course order."""
    wanted = concepts or VERTICAL_SLICE
    modules = {m["module_id"]: m for m in load_curriculum()["modules"]}
    missing = [c for c in wanted if c not in modules]
    if missing:
        raise ValueError(f"Unknown curriculum modules: {missing}")
    return sorted((modules[c] for c in wanted), key=lambda m: m["order"])
