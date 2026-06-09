from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Student
from ..schemas import StudentProfileIn, StudentProfileOut

router = APIRouter(tags=["students"])


@router.post("/students", status_code=201, response_model=StudentProfileOut)
def create_student(payload: StudentProfileIn, db: Session = Depends(get_db)):
    student = Student(name=payload.name, profile=payload.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return StudentProfileOut(id=student.id, **payload.model_dump())


@router.get("/students/{student_id}", response_model=StudentProfileOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(404, "student not found")
    return StudentProfileOut(id=student.id, **student.profile)
