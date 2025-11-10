"""SQLAlchemy models."""

from sqlalchemy import Column, Integer, String

from app.db import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(300), nullable=True)
    status = Column(String(20), nullable=False, default="draft")
