from pydantic import BaseModel, validator
from models.users import Users
from db import SessionLocal
from fastapi import HTTPException

db = SessionLocal()


class CreateUser(BaseModel):
    name: str
    username: str
    password: str

    @validator('username')
    def username_validate(cls, username):
        validate_my = db.query(Users).filter(
            Users.username == username,
        ).count()

        if validate_my != 0:
            raise HTTPException(400, 'This login has already been registered !!!')
        return username

    @validator('password')
    def password_validate(cls, password):
        if len(password) < 8:
            raise HTTPException(400, 'Password should not be less than 8 characters')
        return password


class UpdateUser(BaseModel):
    name: str
    password: str

    @validator('password')
    def password_validate(cls, password):
        if len(password) < 8:
            raise HTTPException(400, 'Password should not be less than 8 characters')
        return password
