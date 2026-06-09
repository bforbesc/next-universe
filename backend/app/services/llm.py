"""LLM content generation via the Anthropic API.

Design rules (from the product spec):
- The LLM never generates game code — it fills the StoryArc / Mission schemas.
- Output is structured (client.messages.parse + Pydantic), then re-validated
  and test-verified by the caller before anything is persisted.
- The baseline curriculum is embedded verbatim in every prompt: the model
  transforms and personalizes the course, it does not invent it.
"""
from __future__ import annotations

import json

from .. import config
from ..schemas import MissionWithSolution, StoryArc, StudentProfileIn


def llm_available() -> bool:
    return bool(config.ANTHROPIC_API_KEY)


def _client():
    import anthropic

    return anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def _profile_block(profile: StudentProfileIn) -> str:
    return json.dumps(profile.model_dump(), indent=2)


def _module_block(module: dict) -> str:
    return json.dumps(
        {
            "module_id": module["module_id"],
            "title": module["title"],
            "learning_objectives": module["learning_objectives"],
            "explanation": module["explanation"],
            "examples": module["examples"],
            "common_mistakes": module.get("common_mistakes", []),
            "exercise_patterns": module.get("exercise_patterns", []),
            "difficulty": module["difficulty"],
        },
        indent=2,
    )


STORYTELLING_RULES = """
Storytelling requirements (non-negotiable):
- A clear protagonist (the student), a world with rules, a motivating central
  conflict, and rising stakes across the mission arc.
- A mentor character with a distinct voice who frames every mission.
- Every coding challenge must MATTER inside the story: the Python concept is
  the in-world mechanism (variables store vital resources, conditionals make
  survival decisions, loops automate repeated work, lists manage inventories,
  dictionaries hold structured records, functions are reusable tools).
- The story must read as one continuous arc with payoff, never as a quiz with
  decoration.
"""


def build_story_arc_prompt(profile: StudentProfileIn, modules: list[dict]) -> str:
    module_summaries = "\n".join(
        f"- {m['module_id']}: {m['title']} (difficulty {m['difficulty']}) — objectives: "
        + "; ".join(m["learning_objectives"])
        for m in modules
    )
    return f"""You are the narrative designer of an educational game platform.
Design a personalized story arc that teaches Python through a story world.

STUDENT PROFILE:
{_profile_block(profile)}

BASELINE CURRICULUM (the course already exists — your arc must teach exactly
these modules, in this order, one mission per module):
{module_summaries}

{STORYTELLING_RULES}

Theme: derive it from the student's preferred_theme if set, otherwise from
their interests. The world, characters and stakes must feel made for THIS
student (use their name and interests), and must be age-appropriate.

Produce a StoryArc. mission_arc must contain exactly {len(modules)} entries
whose python_concept values are exactly {[m['module_id'] for m in modules]}
in that order, with mission_id values m1-<concept>, m2-<concept>, ...
"""


def build_mission_prompt(
    profile: StudentProfileIn,
    arc: StoryArc,
    module: dict,
    previous_state: str | None,
) -> str:
    continuity = (
        f'The previous mission ended with: "{previous_state}"\n'
        "story_context.previous_state MUST continue from exactly that moment."
        if previous_state
        else "This is the FIRST mission: previous_state must set the opening scene of the conflict."
    )
    return f"""You are the mission designer of an educational game platform.
Write one playable mission that teaches one Python concept inside the story.

STUDENT PROFILE:
{_profile_block(profile)}

STORY ARC (already approved — stay strictly inside this world):
{arc.model_dump_json(indent=2)}

BASELINE CURRICULUM MODULE (this is the existing course content; transform and
personalize it — teach exactly this, do not invent different material):
{_module_block(module)}

NARRATIVE CONTINUITY:
{continuity}

{STORYTELLING_RULES}

Engineering contract for the exercise:
- starter_code: runnable scaffold with story-voiced comments; any given data
  (sensor readings, lists) is defined here and marked "do not change".
- student_task: precise, beginner-readable, names every variable the tests check.
- hidden_tests: 2-4 entries. Each `assertion` is a PYTHON BOOLEAN EXPRESSION
  evaluated in the namespace AFTER the student's code runs (e.g.
  "oxygen_level == 100"). Never English prose, never statements. Each
  `description` explains the check in story terms without revealing the answer.
- reference_solution: a complete program (including the given data) that makes
  every assertion True. It will be executed to verify your tests — if it fails,
  the mission is rejected.
- hints: exactly 3, escalating: concept nudge -> structure -> near-solution.
- remediation: a simpler explanation plus a strictly smaller first subtask.
- success/failure feedback: technical_feedback teaches; story_feedback advances
  or stalls the story in the mentor's voice.
- The exercise must only require concepts from this module or earlier ones.
- Retrieval practice: where natural, the exercise should ALSO exercise one
  concept from an earlier module in service of the new one (e.g. a loops
  mission still assigns and updates variables) — never a later concept.
- Difficulty: respect the student's difficulty_preference ({profile.difficulty_preference}).

Produce a MissionWithSolution for module "{module['module_id']}".
"""


def generate_story_arc(profile: StudentProfileIn, modules: list[dict]) -> StoryArc:
    response = _client().messages.parse(
        model=config.ANTHROPIC_MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": build_story_arc_prompt(profile, modules)}],
        output_format=StoryArc,
    )
    arc = response.parsed_output
    if arc is None:
        raise ValueError("story arc generation returned no parsable output")
    expected = [m["module_id"] for m in modules]
    actual = [e.python_concept for e in arc.mission_arc]
    if actual != expected:
        raise ValueError(f"arc concepts {actual} do not match curriculum {expected}")
    return arc


def generate_mission(
    profile: StudentProfileIn,
    arc: StoryArc,
    module: dict,
    previous_state: str | None,
    mission_id: str,
) -> MissionWithSolution:
    response = _client().messages.parse(
        model=config.ANTHROPIC_MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        messages=[
            {
                "role": "user",
                "content": build_mission_prompt(profile, arc, module, previous_state),
            }
        ],
        output_format=MissionWithSolution,
    )
    mission = response.parsed_output
    if mission is None:
        raise ValueError(f"mission generation for {mission_id} returned no parsable output")
    # Canonical identity fields are owned by the engine, not the model.
    mission.mission_id = mission_id
    mission.module = module["module_id"]
    mission.theme = arc.theme
    if previous_state:
        mission.story_context.previous_state = previous_state
    return mission


def generate_llm_adventure(
    profile: StudentProfileIn, modules: list[dict]
) -> tuple[StoryArc, list[MissionWithSolution]]:
    arc = generate_story_arc(profile, modules)
    missions: list[MissionWithSolution] = []
    previous_state: str | None = None
    for idx, module in enumerate(modules):
        mission = generate_mission(
            profile, arc, module, previous_state, mission_id=f"m{idx + 1}-{module['module_id']}"
        )
        missions.append(mission)
        # Chain the narrative: the next mission opens where success ended.
        previous_state = mission.success_feedback.story_feedback
    return arc, missions
