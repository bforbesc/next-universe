from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Adventure, MissionState, Student
from ..schemas import AdventureCreate, AdventureOut, MissionProgress, ProgressOut, StudentProfileIn
from ..services import generator
from ..services.curriculum import get_modules

router = APIRouter(tags=["adventures"])


@router.post("/adventures", status_code=201, response_model=AdventureOut)
def create_adventure(payload: AdventureCreate, db: Session = Depends(get_db)):
    student = db.get(Student, payload.student_id)
    if student is None:
        raise HTTPException(404, "student not found")
    try:
        modules = get_modules(payload.course_id, payload.concepts)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(422, str(exc))

    profile = StudentProfileIn(**student.profile)
    generator_name, arc, missions = generator.create_adventure(profile, modules)

    adventure = Adventure(
        student_id=student.id,
        generator=generator_name,
        format="mission-map-2d",
        story_arc=arc.model_dump(),
        # reference_solution is stored for audit/reproducibility; the API
        # response model (Mission) strips it before it reaches the client.
        missions=[m.model_dump() for m in missions],
    )
    db.add(adventure)
    db.commit()
    db.refresh(adventure)
    for m in missions:
        db.add(MissionState(adventure_id=adventure.id, mission_id=m.mission_id))
    db.commit()
    return _to_out(adventure)


@router.get("/adventures/{adventure_id}", response_model=AdventureOut)
def get_adventure(adventure_id: int, db: Session = Depends(get_db)):
    adventure = db.get(Adventure, adventure_id)
    if adventure is None:
        raise HTTPException(404, "adventure not found")
    return _to_out(adventure)


@router.get("/adventures/{adventure_id}/progress", response_model=ProgressOut)
def get_progress(adventure_id: int, db: Session = Depends(get_db)):
    adventure = db.get(Adventure, adventure_id)
    if adventure is None:
        raise HTTPException(404, "adventure not found")
    states = {
        s.mission_id: s
        for s in db.query(MissionState).filter_by(adventure_id=adventure_id).all()
    }
    missions: list[MissionProgress] = []
    unlocked = True  # the first incomplete mission is available, the rest locked
    for m in adventure.missions:
        state = states.get(m["mission_id"])
        completed = bool(state and state.completed)
        if completed:
            status = "completed"
        elif unlocked:
            status = "available"
            unlocked = False
        else:
            status = "locked"
        missions.append(
            MissionProgress(
                mission_id=m["mission_id"],
                status=status,
                attempts=state.attempts if state else 0,
            )
        )
    completed_count = sum(1 for m in missions if m.status == "completed")
    return ProgressOut(
        adventure_id=adventure_id,
        missions=missions,
        completed_count=completed_count,
        total_count=len(missions),
    )


def _to_out(adventure: Adventure) -> AdventureOut:
    return AdventureOut(
        id=adventure.id,
        student_id=adventure.student_id,
        generator=adventure.generator,
        format=adventure.format,
        story_arc=adventure.story_arc,
        missions=adventure.missions,
    )
