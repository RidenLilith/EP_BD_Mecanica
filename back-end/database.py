# backend/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use env var DATABASE_URL; cai pro SQLite se não setar (útil p/ rodar fora do Docker)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(
    DATABASE_URL, 
    echo=False, 
    future=True,
    pool_size=20,           # Aumentar tamanho do pool
    max_overflow=40,        # Permitir mais conexões em overflow
    pool_pre_ping=True,     # Testar conexões antes de usar
    pool_recycle=3600       # Reciclar conexões a cada hora
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
