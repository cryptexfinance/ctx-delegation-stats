from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import DATABASE_URL
Base = declarative_base()

engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine)

