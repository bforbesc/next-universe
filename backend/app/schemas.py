"""Pydantic contracts for everything that crosses the API boundary.

StoryArc and Mission are the schemas the LLM must fill. The game engine only
ever consumes validated instances of these models, never raw LLM text.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Student profile
# ---------------------------------------------------------------------------

class StudentProfileIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    age: Optional[int] = Field(default=None, ge=5, le=120)
    interests: list[str] = Field(default_factory=list, max_length=10)
    prior_knowledge: Literal["none", "some", "comfortable"] = "none"
    preferred_theme: Optional[str] = None
    learning_goal: Optional[str] = Field(default=None, max_length=300)
    difficulty_preference: Literal["gentle", "standard", "challenging"] = "standard"


class StudentProfileOut(StudentProfileIn):
    id: int


# ---------------------------------------------------------------------------
# Story arc (one per adventure) — mirrors the product spec schema
# ---------------------------------------------------------------------------

class MentorCharacter(BaseModel):
    name: str
    role: str
    personality: str


class MissionArcEntry(BaseModel):
    mission_id: str
    python_concept: str
    story_purpose: str
    learning_objective: str
    difficulty: int = Field(ge=1, le=5)


class FinalChallenge(BaseModel):
    description: str
    concepts_combined: list[str]


class StoryArc(BaseModel):
    student_profile_summary: str
    course_topic: str = "Beginner Python"
    theme: str
    story_title: str
    protagonist_role: str
    world_description: str
    central_conflict: str
    main_goal: str
    mentor_character: MentorCharacter
    mission_arc: list[MissionArcEntry]
    final_challenge: FinalChallenge


# ---------------------------------------------------------------------------
# Mission — mirrors the product spec schema
# ---------------------------------------------------------------------------

class StoryContext(BaseModel):
    previous_state: str
    current_problem: str
    why_this_matters: str
    narrative_stakes: str


class HiddenTest(BaseModel):
    """One deterministic check, expressed as a Python assertion.

    The assertion runs in the same namespace as the student's code, so it can
    reference any variable or function the task asks the student to define.
    `description` is shown to the student only after the test runs (pass/fail),
    never the assertion source itself.
    """

    assertion: str
    description: str


class Feedback(BaseModel):
    technical_feedback: str
    story_feedback: str


class Remediation(BaseModel):
    simpler_explanation: str
    smaller_subtask: str


class NextMissionRules(BaseModel):
    on_success: Literal["next", "finish"] = "next"
    on_failure: Literal["remediate", "retry"] = "remediate"


class Mission(BaseModel):
    mission_id: str
    module: str
    difficulty: int = Field(ge=1, le=5)
    theme: str
    title: str
    story_context: StoryContext
    learning_objective: str
    concept_explanation: str
    starter_code: str
    student_task: str
    expected_solution_description: str
    hidden_tests: list[HiddenTest] = Field(min_length=1)
    hints: list[str] = Field(min_length=3, max_length=5)
    success_feedback: Feedback
    failure_feedback: Feedback
    remediation: Remediation
    next_mission_rules: NextMissionRules = NextMissionRules()


# ---------------------------------------------------------------------------
# Adventure (a generated, persisted playthrough)
# ---------------------------------------------------------------------------

class AdventureCreate(BaseModel):
    student_id: int
    concepts: Optional[list[str]] = None  # default: vertical slice


class AdventureOut(BaseModel):
    id: int
    student_id: int
    generator: Literal["llm", "template"]
    story_arc: StoryArc
    missions: list[Mission]


# ---------------------------------------------------------------------------
# Submissions & progress
# ---------------------------------------------------------------------------

class SubmissionIn(BaseModel):
    adventure_id: int
    mission_id: str
    code: str = Field(max_length=20_000)
    passed: bool
    test_results: list[dict] = Field(default_factory=list)
    error: Optional[str] = None


class SubmissionResult(BaseModel):
    recorded: bool
    passed: bool
    attempts: int
    next_action: Literal["next", "finish", "retry", "remediate"]
    hint_level: int
    hint: Optional[str] = None
    technical_feedback: str
    story_feedback: str
    remediation: Optional[Remediation] = None


class MissionProgress(BaseModel):
    mission_id: str
    status: Literal["locked", "available", "completed"]
    attempts: int


class ProgressOut(BaseModel):
    adventure_id: int
    missions: list[MissionProgress]
    completed_count: int
    total_count: int
