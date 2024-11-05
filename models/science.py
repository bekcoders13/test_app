from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db import Base
from models.users import Users


class Sciences(Base):
    __tablename__ = "sciences"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(255), nullable=False)
    user_id = Column(Integer, nullable=False)

    user = relationship("Users", foreign_keys=[user_id],
                        primaryjoin=lambda: Users.id == Sciences.user_id)
