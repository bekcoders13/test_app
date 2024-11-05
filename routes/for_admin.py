import inspect
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session, load_only
from datetime import datetime, timedelta

from db import database
from functions.db_operations import get_in_db
from functions.role_verification import role_verification
from models.answer import Answers
from models.question import Questions
from models.science import Sciences
from routes.login import get_current_active_user
from schemas.users import CreateUser

admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin operations"]
)


@admin_router.get('/get_science')
async def get_science(db: Session = Depends(database),
                      current_user: CreateUser = Depends(get_current_active_user)):
    await role_verification(current_user, inspect.currentframe().f_code.co_name)
    return db.query(Sciences).all()


@admin_router.get('/get_full_test')
async def get(science_id: int = 0, db: Session = Depends(database),
              current_user: CreateUser = Depends(get_current_active_user)):
    await role_verification(current_user, inspect.currentframe().f_code.co_name)
    await get_in_db(db, Sciences, science_id)
    questions = (db.query(Questions).options(load_only(Questions.text))
                 .filter(Questions.science_id == science_id).all())
    result1 = []
    for question in questions:
        answers = db.query(Answers).filter(Answers.question_id == question.id).all()
        result1.append({
            "question": question,
            "answers": [answer for answer in answers]
        })

    return {"data": result1}


@admin_router.delete('/delete_test')
async def delete_test_f(interval: int, db: Session = Depends(database),
                        current_user: CreateUser = Depends(get_current_active_user)):
    await role_verification(current_user, inspect.currentframe().f_code.co_name)

    cutoff_time = datetime.now() - timedelta(days=interval)
    questions = db.query(Questions).filter(Questions.created_at < cutoff_time).all()

    for question in questions:
        db.query(Answers).filter(Answers.question_id == question.id).delete()
        db.query(Questions).filter(Questions.id == question.id).delete()

    db.commit()
    return {"message": f"{len(questions)} ta eski testlar o'chirildi"}

