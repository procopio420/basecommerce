import json

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# #region agent log
_log_path = "/home/lucas/hobby/construction/.cursor/debug.log"
try:
    with open(_log_path, "a") as f:
        f.write(
            json.dumps(
                {
                    "location": "database.py:9",
                    "message": "Creating database engine",
                    "data": {
                        "database_url": settings.DATABASE_URL[:100]
                        if settings.DATABASE_URL
                        else "None"
                    },
                    "sessionId": "debug-session",
                    "runId": "startup",
                    "hypothesisId": "DB_CONNECTION",
                },
                ensure_ascii=False,
            )
            + "\n"
        )
except Exception:
    pass
# #endregion

engine = create_engine(
    settings.DATABASE_URL, pool_pre_ping=True, echo=False  # Set to True for SQL debugging
)

# #region agent log
_log_path = "/home/lucas/hobby/construction/.cursor/debug.log"
try:
    with open(_log_path, "a") as f:
        f.write(
            json.dumps(
                {
                    "location": "database.py:16",
                    "message": "Database engine created",
                    "data": {
                        "url_parts": settings.DATABASE_URL.split("@")[-1]
                        if "@" in settings.DATABASE_URL
                        else "invalid"
                    },
                    "sessionId": "debug-session",
                    "runId": "startup",
                    "hypothesisId": "DB_CONNECTION",
                },
                ensure_ascii=False,
            )
            + "\n"
        )
except Exception:
    pass
# #endregion

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
