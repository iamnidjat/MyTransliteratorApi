from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# root class for all the ORM models.
class Base(DeclarativeBase):
    pass