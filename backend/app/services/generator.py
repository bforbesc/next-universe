"""Generator orchestration.

LLM-first when configured; every generated adventure (LLM or template) is
schema-validated by construction and test-verified before it is returned.
A generation failure degrades to the template generator — the product never
breaks because a model call did.

Extension point: this is where future game formats and courses plug in — a
format-keyed registry of generators, all returning (StoryArc, missions).
"""
from __future__ import annotations

import logging

from ..schemas import MissionWithSolution, StoryArc, StudentProfileIn
from .code_verify import verify_program
from .fallback import generate_template_adventure
from .llm import generate_llm_adventure, llm_available  # noqa: F401  (patched in tests)

logger = logging.getLogger(__name__)


class ContentVerificationError(Exception):
    pass


def _verify_all(missions: list[MissionWithSolution]) -> None:
    for mission in missions:
        ok, error = verify_program(mission.reference_solution, mission.hidden_tests)
        if not ok:
            raise ContentVerificationError(f"{mission.mission_id}: {error}")


def create_adventure(
    profile: StudentProfileIn, modules: list[dict]
) -> tuple[str, StoryArc, list[MissionWithSolution]]:
    """Returns (generator_name, story_arc, missions) — always verified."""
    if llm_available():
        try:
            arc, missions = generate_llm_adventure(profile, modules)
            _verify_all(missions)
            return "llm", arc, missions
        except Exception:
            logger.exception("LLM generation failed; falling back to template content")

    arc, missions = generate_template_adventure(profile, modules)
    _verify_all(missions)
    return "template", arc, missions
