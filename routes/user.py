import inspect
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from functions.role_verification import role_verification
from functions.user import create_user_f, update_user_f, delete_user_f, create_admin_f
from models.users import Users
from routes.login import get_current_active_user
from schemas.users import CreateUser, UpdateUser
from db import database


users_router = APIRouter(
    prefix="/users",
    tags=["Users operation"]
)


@users_router.get('/get_users')
def get_users(db: Session = Depends(database),
              current_user: CreateUser = Depends(get_current_active_user)):
    role_verification(current_user, inspect.currentframe().f_code.co_name)
    return db.query(Users).all()


@users_router.get('/get_own')
def get_own(current_user: CreateUser = Depends(get_current_active_user)):
    return current_user


@users_router.post('/create_admin')
def create_admin(form: CreateUser, db: Session = Depends(database),
                 current_user: CreateUser = Depends(get_current_active_user)):
    role_verification(current_user, inspect.currentframe().f_code.co_name)
    create_admin_f(form, db, current_user)
    raise HTTPException(status_code=200, detail="Amaliyot muvaffaqiyatli amalga oshirildi !!!")


@users_router.post('/sign_up')
def create_user(form: CreateUser, db: Session = Depends(database)):
    create_user_f(form, db)
    raise HTTPException(status_code=200, detail="Amaliyot muvaffaqiyatli amalga oshirildi !!!")


@users_router.put("/update")
def update_user(form: UpdateUser, db: Session = Depends(database),
                current_user: CreateUser = Depends(get_current_active_user)):
    role_verification(current_user, inspect.currentframe().f_code.co_name)
    update_user_f(form, db, current_user)
    raise HTTPException(status_code=200, detail="Amaliyot muvaffaqiyatli amalga oshirildi !!!")


@users_router.delete("/delete")
def delete_user(db: Session = Depends(database),
                current_user: CreateUser = Depends(get_current_active_user)):
    role_verification(current_user, inspect.currentframe().f_code.co_name)
    delete_user_f(db, current_user)
    raise HTTPException(status_code=200, detail="Amaliyot muvaffaqiyatli amalga oshirildi !!!")


