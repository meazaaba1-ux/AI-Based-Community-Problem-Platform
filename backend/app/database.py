
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# --------------------------------
# DATABASE CONFIGURATION
# --------------------------------

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv(
    "DB_NAME",
    "community_problem_platform"
)

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}/{DB_NAME}"
)


# --------------------------------
# DATABASE ENGINE
# --------------------------------

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# --------------------------------
# DATABASE SESSION
# --------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# --------------------------------
# DATABASE BASE
# --------------------------------

Base = declarative_base()


# --------------------------------
# DATABASE CONNECTION
# --------------------------------

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
