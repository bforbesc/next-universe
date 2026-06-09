from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Adventure, MissionState, Submission
from ..schemas import Mission, Remediation, SubmissionIn, SubmissionResult

router = APIRouter(tags=["submissions"])

REMEDIATION_THRESHOLD = 3


@router.post("/submissions", response_model=SubmissionResult)
def submit(payload: SubmissionIn, db: Session = Depends(get_db)):
    adventure = db.get(Adventure, payload.adventure_id)
    if adventure is None:
        raise HTTPException(404, "adventure not found")

    mission_index = next(
        (i for i, m in enumerate(adventure.missions) if m["mission_id"] == payload.mission_id),
        None,
    )
    if mission_index is None:
        raise HTTPException(404, "mission not found in this adventure")
    mission = Mission.model_validate(adventure.missions[mission_index])

    # Telemetry: every attempt is stored, including the failure patterns.
    db.add(
        Submission(
            adventure_id=adventure.id,
            mission_id=payload.mission_id,
            code=payload.code,
            passed=payload.passed,
            test_results=payload.test_results,
            error=payload.error,
        )
    )
    state = (
        db.query(MissionState)
        .filter_by(adventure_id=adventure.id, mission_id=payload.mission_id)
        .first()
    )
    if state is None:
        state = MissionState(adventure_id=adventure.id, mission_id=payload.mission_id)
        db.add(state)
    state.attempts += 1
    if payload.passed:
        state.completed = True
    db.commit()

    if payload.passed:
        is_last = mission_index == len(adventure.missions) - 1
        return SubmissionResult(
            recorded=True,
            passed=True,
            attempts=state.attempts,
            next_action="finish" if is_last else "next",
            hint_level=0,
            hint=None,
            technical_feedback=mission.success_feedback.technical_feedback,
            story_feedback=mission.success_feedback.story_feedback,
            remediation=None,
        )

    # Failure path: escalate hints, then offer remediation.
    hint_level = min(state.attempts, len(mission.hints))
    needs_remediation = state.attempts >= REMEDIATION_THRESHOLD
    return SubmissionResult(
        recorded=True,
        passed=False,
        attempts=state.attempts,
        next_action="remediate" if needs_remediation else "retry",
        hint_level=hint_level,
        hint=mission.hints[hint_level - 1],
        technical_feedback=mission.failure_feedback.technical_feedback,
        story_feedback=mission.failure_feedback.story_feedback,
        remediation=Remediation(**mission.remediation.model_dump()) if needs_remediation else None,
    )
