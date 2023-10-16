from sqlalchemy import Boolean, Column, Date, Integer, String

from backend.db import Base


class User(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    birthdate = Column(Date)
    bio = Column(String)
    city = Column(String)
    country = Column(String)
    password = Column(String)
    disabled = Column(Boolean)
