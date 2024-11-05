from sqlalchemy import Integer, Column, String, Date
from sqlalchemy.orm import relationship

from db import Base
from models.science import Sciences
from models.users import Users


class Questions(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(255), nullable=False)
    created_at = Column(Date, nullable=False)
    science_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)

    user = relationship("Users", foreign_keys=[user_id],
                        primaryjoin=lambda: Users.id == Questions.user_id)

    science = relationship("Sciences", foreign_keys=[science_id],
                           primaryjoin=lambda: Sciences.id == Questions.science_id)
