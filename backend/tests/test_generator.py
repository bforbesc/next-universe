"""Generator orchestration: LLM-first when configured, always schema-validated,
always test-verified, never lets a generation failure break the product."""
import pytest

from app.schemas import StudentProfileIn
from app.services import generator
from app.services.curriculum import VERTICAL_SLICE, get_modules

MODULES = get_modules("python-beginner", VERTICAL_SLICE)
PROFILE = StudentProfileIn(name="Ada", age=12, interests=["space"])


def test_without_api_key_uses_template_generator(monkeypatch):
    monkeypatch.setattr(generator, "llm_available", lambda: False)
    name, arc, missions = generator.create_adventure(PROFILE, MODULES)
    assert name == "template"
    assert len(missions) == len(MODULES)


def test_llm_failure_falls_back_to_template(monkeypatch):
    monkeypatch.setattr(generator, "llm_available", lambda: True)

    def boom(*args, **kwargs):
        raise RuntimeError("model unavailable")

    monkeypatch.setattr(generator, "generate_llm_adventure", boom)
    name, arc, missions = generator.create_adventure(PROFILE, MODULES)
    assert name == "template"
    assert len(missions) == len(MODULES)


def test_llm_content_failing_verification_falls_back(monkeypatch):
    """If the LLM writes hidden tests its own reference solution can't pass,
    we refuse the content rather than shipping a broken mission."""
    monkeypatch.setattr(generator, "llm_available", lambda: True)

    def broken_content(profile, modules):
        _, missions = generator.generate_template_adventure(profile, modules)
        arc, _ = generator.generate_template_adventure(profile, modules)
        missions[0].reference_solution = "completely = 'wrong'"
        return arc, missions

    monkeypatch.setattr(generator, "generate_llm_adventure", broken_content)
    name, _, _ = generator.create_adventure(PROFILE, MODULES)
    assert name == "template"


def test_verified_llm_content_is_used(monkeypatch):
    monkeypatch.setattr(generator, "llm_available", lambda: True)
    monkeypatch.setattr(
        generator,
        "generate_llm_adventure",
        lambda profile, modules: generator.generate_template_adventure(profile, modules),
    )
    name, _, missions = generator.create_adventure(PROFILE, MODULES)
    assert name == "llm"
    assert len(missions) == len(MODULES)


def test_llm_prompts_embed_baseline_curriculum():
    """Core product requirement: the LLM transforms the existing course content,
    it does not invent the course."""
    from app.services import llm

    arc_prompt = llm.build_story_arc_prompt(PROFILE, MODULES)
    for module in MODULES:
        assert module["title"] in arc_prompt

    mission_prompt = llm.build_mission_prompt(
        PROFILE,
        generator.generate_template_adventure(PROFILE, MODULES)[0],
        MODULES[0],
        previous_state=None,
    )
    # the baseline explanation and objectives must reach the model verbatim
    assert MODULES[0]["explanation"] in mission_prompt
    for objective in MODULES[0]["learning_objectives"]:
        assert objective in mission_prompt
