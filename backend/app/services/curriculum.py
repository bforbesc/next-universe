"""Loads baseline curricula. Courses are data, not code: adding a course means
adding a curriculum file, never touching the engine. The generator personalizes
*this* content — it never invents the course."""
import json
from functools import lru_cache

from ..config import CURRICULUM_DIR

VERTICAL_SLICE = ["variables", "conditionals", "loops"]


@lru_cache(maxsize=None)
def load_curriculum(course_id: str) -> dict:
    path = CURRICULUM_DIR / f"{course_id.replace('-', '_')}.json"
    if not path.exists():
        raise FileNotFoundError(f"No curriculum file for course '{course_id}' at {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_modules(course_id: str, concepts: list[str] | None = None) -> list[dict]:
    """Return curriculum modules for the requested concepts, in course order."""
    wanted = concepts or VERTICAL_SLICE
    modules = {m["module_id"]: m for m in load_curriculum(course_id)["modules"]}
    missing = [c for c in wanted if c not in modules]
    if missing:
        raise ValueError(f"Unknown curriculum modules: {missing}")
    return sorted((modules[c] for c in wanted), key=lambda m: m["order"])
