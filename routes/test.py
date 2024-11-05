import inspect
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session, load_only

from db import database
from functions.create_test import create_result_f
from functions.db_operations import save_in_db, get_in_db
from functions.role_verification import role_verification
from models.answer import Answers
from models.question import Questions
from models.science import Sciences
from routes.login import get_current_active_user
from schemas.result import AddResult
from typing import List

from schemas.users import CreateUser

tests_router = APIRouter(
    prefix="/test",
    tags=["Mening testlarim"]
)


@tests_router.post('/add_science')
async def create_science(science_name: str, db: Session = Depends(database),
                         current_user: CreateUser = Depends(get_current_active_user)):
    await role_verification(current_user, inspect.currentframe().f_code.co_name)
    new_item = Sciences(
        name=science_name,
        user_id=current_user.id
    )
    save_in_db(db, new_item)
    raise HTTPException(200, 'success')


@tests_router.get('/get_science')
async def get_science(db: Session = Depends(database),
                      current_user: CreateUser = Depends(get_current_active_user)):
    await role_verification(current_user, inspect.currentframe().f_code.co_name)
    return db.query(Sciences).filter(Sciences.user_id == current_user.id).all()


@tests_router.get('/get__my_tests')
async def get_test_f(science_id: int, db: Session = Depends(database),
                     current_user: CreateUser = Depends(get_current_active_user)):
    await role_verification(current_user, inspect.currentframe().f_code.co_name)
    await get_in_db(db, Sciences, science_id)
    questions = (db.query(Questions).options(load_only(Questions.text))
                 .filter(Questions.science_id == science_id,
                         Questions.user_id == current_user.id).all())
    result1 = []
    for question in questions:
        answers = db.query(Answers).filter(Answers.question_id == question.id).all()
        result1.append({
            "question": question,
            "answers": [answer for answer in answers]
        })

    return {"data": result1}


@tests_router.post('/upload_test/{science_id}')
async def upload_txt(science_id: int, file: UploadFile = File(...), db: Session = Depends(database),
                     current_user: CreateUser = Depends(get_current_active_user)):
    await role_verification(current_user, inspect.currentframe().f_code.co_name)
    item = await create_result_f(db, science_id, file, current_user)
    return item


@tests_router.post('/add_result')
async def result(forms: List[AddResult], db: Session = Depends(database),
                 current_user: CreateUser = Depends(get_current_active_user)):
    await role_verification(current_user, inspect.currentframe().f_code.co_name)
    total = 0
    common = 0

    for form in forms:
        sc = await get_in_db(db, Questions, form.question_id)
        if sc.user_id != current_user.id:
            raise HTTPException(400, "siz o'zingizga tegishli bo'lmagan testni ishladingiz")

        await get_in_db(db, Answers, form.answer_id)
        answer = db.query(Answers).filter(Answers.id == form.answer_id).first()
        total += 1
        if answer.status:
            common += 1
    return {"jami savollar soni": total,
            "to`g`ri javoblar soni": common}


@tests_router.delete('/delete_my_tests')
async def delete_my_test_f(science_id: int, db: Session = Depends(database),
                           current_user: CreateUser = Depends(get_current_active_user)):
    await role_verification(current_user, inspect.currentframe().f_code.co_name)
    await get_in_db(db, Sciences, science_id)
    questions = db.query(Questions).filter(Questions.science_id == science_id,
                                           Questions.user_id == current_user.id).all()
    for question in questions:
        db.query(Questions).filter(Questions.id == question.id).delete()

        answers = db.query(Answers).filter(Answers.question_id == question.id).all()
        for answer in answers:
            db.query(Answers).filter(Answers.id == answer.id).delete()
    db.query(Sciences).filter(Sciences.id == science_id).delete()
    db.commit()
    raise HTTPException(200, 'Success')
