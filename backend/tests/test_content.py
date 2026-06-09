"""Golden-content tests: the template generator's output must satisfy the same
schema and quality bars we demand from the LLM. These templates double as
few-shot examples for the LLM and as the no-API-key fallback."""
import pytest

from app.schemas import Mission, StoryArc, StudentProfileIn
from app.services.code_verify import verify_program
from app.services.curriculum import VERTICAL_SLICE, get_modules
from app.services.fallback import THEMES, generate_template_adventure

MODULES = get_modules("python-beginner", VERTICAL_SLICE)


def profile_for(interest: str) -> StudentProfileIn:
    return StudentProfileIn(name="Ada", age=12, interests=[interest])


@pytest.mark.parametrize("theme", list(THEMES))
def test_every_theme_produces_schema_valid_content(theme):
    arc, missions = generate_template_adventure(profile_for(theme), MODULES)
    assert isinstance(arc, StoryArc)
    assert arc.theme == theme
    assert len(missions) == len(MODULES)
    for m in missions:
        assert isinstance(m, Mission)  # MissionWithSolution subclasses Mission


@pytest.mark.parametrize("theme", list(THEMES))
def test_reference_solutions_pass_their_own_hidden_tests(theme):
    _, missions = generate_template_adventure(profile_for(theme), MODULES)
    for m in missions:
        ok, error = verify_program(m.reference_solution, m.hidden_tests)
        assert ok, f"{theme}/{m.mission_id}: {error}"


def test_missions_match_arc_and_curriculum_order():
    arc, missions = generate_template_adventure(profile_for("space"), MODULES)
    assert [e.python_concept for e in arc.mission_arc] == [m["module_id"] for m in MODULES]
    assert [m.module for m in missions] == [m_["module_id"] for m_ in MODULES]
    assert [m.mission_id for m in missions] == [e.mission_id for e in arc.mission_arc]


def test_story_continuity_between_missions():
    """Mission N+1's previous_state must carry forward mission N's outcome —
    the story is a chain, not isolated quiz wrappers."""
    _, missions = generate_template_adventure(profile_for("space"), MODULES)
    for prev, nxt in zip(missions, missions[1:]):
        assert len(nxt.story_context.previous_state) > 20
        # success story feedback should be reflected in the next mission's state
        assert nxt.story_context.previous_state == prev.success_feedback.story_feedback


def test_interest_matching_picks_a_relevant_theme():
    arc, _ = generate_template_adventure(
        StudentProfileIn(name="Leo", interests=["football", "FC Porto"]), MODULES
    )
    assert arc.theme == "football"


def test_unknown_interest_falls_back_to_generic_theme():
    arc, _ = generate_template_adventure(
        StudentProfileIn(name="Sam", interests=["competitive knitting"]), MODULES
    )
    assert arc.theme in THEMES  # still a valid theme, never a crash


def test_explicit_theme_preference_wins_over_interests():
    arc, _ = generate_template_adventure(
        StudentProfileIn(name="Mia", interests=["football"], preferred_theme="music"),
        MODULES,
    )
    assert arc.theme == "music"


def test_personalization_reaches_the_story_text():
    arc, missions = generate_template_adventure(profile_for("space"), MODULES)
    blob = arc.model_dump_json() + "".join(m.model_dump_json() for m in missions)
    assert "Ada" in blob  # the student's name is woven into the narrative


def test_difficulty_preference_shifts_mission_difficulty():
    _, gentle = generate_template_adventure(
        StudentProfileIn(name="A", interests=["space"], difficulty_preference="gentle"),
        MODULES,
    )
    _, hard = generate_template_adventure(
        StudentProfileIn(name="A", interests=["space"], difficulty_preference="challenging"),
        MODULES,
    )
    assert sum(m.difficulty for m in hard) > sum(m.difficulty for m in gentle)


def test_missions_have_escalating_hints_and_remediation():
    _, missions = generate_template_adventure(profile_for("music"), MODULES)
    for m in missions:
        assert 3 <= len(m.hints) <= 5
        assert m.remediation.simpler_explanation
        assert m.remediation.smaller_subtask
        assert m.concept_explanation  # teaching content present, not just story
