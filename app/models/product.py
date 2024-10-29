from app.db.base import Base
from sqlalchemy import Column, Integer, String


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String)
    tags = Column(String)
