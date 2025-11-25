# back-end/database.py
import os
import json
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1) Tenta ler local_config.json na raiz do projeto
cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "local_config.json")
DATABASE_URL = None

if os.path.exists(cfg_path):
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    db = cfg.get("db") or {}
    dialect = db.get("dialect", "postgresql")
    user = db.get("user") or "postgres"
    password = db.get("password") or ""
    host = db.get("host") or "localhost"
    port = db.get("port") or 5432
    database = db.get("database") or "teste"

    user_enc = quote_plus(user)
    password_enc = quote_plus(password)
    DATABASE_URL = f"{dialect}://{user_enc}:{password_enc}@{host}:{port}/{database}"
else:
    # 2) SE não tiver local_config.json, cai num default fixo
    DATABASE_URL = "postgresql://postgres:root@localhost:5432/teste"

# 3) Se ainda assim não tiver URL, estoura erro
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não configurada. "
        "Crie local_config.json na raiz do projeto."
    )

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
