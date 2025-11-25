# backend/database.py
import os
import json
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


env_db = os.getenv("DATABASE_URL")
DATABASE_URL = None
if env_db:
    DATABASE_URL = env_db
else:
    cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "local_config.json")
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            db = cfg.get("db") or {}
            dialect = db.get("dialect", "postgresql")
            user = db.get("user") or "postgres"
            password = db.get("password") or ""
            host = db.get("host") or "localhost"
            port = db.get("port") or 5432
            database = db.get("database") or "ep_bd"
            if dialect.startswith("sqlite"):
                DATABASE_URL = f"sqlite:///{database}"
            else:
                user_enc = quote_plus(user)
                password_enc = quote_plus(password)
                DATABASE_URL = f"{dialect}://{user_enc}:{password_enc}@{host}:{port}/{database}"
        except Exception:
            DATABASE_URL = None

if not DATABASE_URL:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=20,           
    max_overflow=40,        
    pool_pre_ping=True,     
    pool_recycle=3600       
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
