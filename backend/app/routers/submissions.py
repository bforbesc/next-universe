from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Adventure, MissionState, Submission
from ..schemas import Mission, SubmissionIn, SubmissionResult
from ..services.progression import evaluate_submission

router = APIRouter(tags=["submissions"])


@router.post("/submissions", response_model=SubmissionResult)
def submit(payload: SubmissionIn, db: Session = Depends(get_db)):
    adventure = db.get(Adventure, payload.adventure_id)
    if adventure is None:
        raise HTTPException(404, "adventure not found")

    mission_data = next(
        (m for m in adventure.missions if m["mission_id"] == payload.mission_id), None
    )
    if mission_data is None:
        raise HTTPException(404, "mission not found in this adventure")
    mission = Mission.model_validate(mission_data)

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

    return evaluate_submission(mission, payload.passed, state.attempts)
