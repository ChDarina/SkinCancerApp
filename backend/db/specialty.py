from sqlalchemy import Column, Integer, String
from db.base import Base, engine


class Specialty(Base):
    __tablename__ = 'Specialty'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

