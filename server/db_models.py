import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    id = Column(String, primary_key=True, index=True)
    email = Column(String)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
