# backend/models.py
from sqlalchemy import Column, Integer, String
from database import Base

class Item(Base):
    __tablename__ = "itens"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    descricao = Column(String(255))
