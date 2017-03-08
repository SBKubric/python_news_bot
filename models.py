from sqlalchemy.engine import create_engine, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Date

engine = create_engine('sqlite:///data.db')
Base = declarative_base()


class Post(Base):
    __tablename__ = 'posts'
    _id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer)
    owner_id = Column(Integer)
    description = Column(String)
    url = Column(String)
    likes_count = Column(Integer)
    created_at = Column(Date)


def initialize_db() -> Engine:
    Base.metadata.create_all(engine)
    return engine
