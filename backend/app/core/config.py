import json
import os

from pydantic import field_validator
from pydantic_settings import BaseSettings

# #region agent log
_log_path = "/home/lucas/hobby/construction/.cursor/debug.log"
try:
    with open(_log_path, "a") as f:
        f.write(
            json.dumps(
                {
                    "location": "config.py:8",
                    "message": "Config module loading",
                    "data": {"env_cors": os.getenv("CORS_ORIGINS")},
                    "sessionId": "debug-session",
                    "runId": "startup",
                    "hypothesisId": "CORS_PARSE",
                },
                ensure_ascii=False,
            )
            + "\n"
        )
except Exception:
    pass
# #endregion


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    CORS_ORIGINS: list[str] | str = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        # #region agent log
        _log_path = "/home/lucas/hobby/construction/.cursor/debug.log"
        try:
            with open(_log_path, "a") as f:
                f.write(
                    json.dumps(
                        {
                            "location": "config.py:26",
                            "message": "CORS validator called",
                            "data": {"value_type": type(v).__name__, "value": str(v)[:100]},
                            "sessionId": "debug-session",
                            "runId": "startup",
                            "hypothesisId": "CORS_PARSE",
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        except Exception:
            pass
        # #endregion
        if isinstance(v, str):
            # Se for string separada por vírgulas, converte em lista
            result = [origin.strip() for origin in v.split(",") if origin.strip()]
            # #region agent log
            _log_path = "/home/lucas/hobby/construction/.cursor/debug.log"
            try:
                with open(_log_path, "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "location": "config.py:32",
                                "message": "CORS parsed from string",
                                "data": {"result": result},
                                "sessionId": "debug-session",
                                "runId": "startup",
                                "hypothesisId": "CORS_PARSE",
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
            except Exception:
                pass
            # #endregion
            return result
        # #region agent log
        _log_path = "/home/lucas/hobby/construction/.cursor/debug.log"
        try:
            with open(_log_path, "a") as f:
                f.write(
                    json.dumps(
                        {
                            "location": "config.py:38",
                            "message": "CORS returning as-is (not string)",
                            "data": {"result_type": type(v).__name__},
                            "sessionId": "debug-session",
                            "runId": "startup",
                            "hypothesisId": "CORS_PARSE",
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        except Exception:
            pass
        # #endregion
        return v

    class Config:
        env_file = ".env"


# #region agent log
_log_path = "/home/lucas/hobby/construction/.cursor/debug.log"
try:
    with open(_log_path, "a") as f:
        f.write(
            json.dumps(
                {
                    "location": "config.py:48",
                    "message": "Creating Settings instance",
                    "data": {},
                    "sessionId": "debug-session",
                    "runId": "startup",
                    "hypothesisId": "SETTINGS_INIT",
                },
                ensure_ascii=False,
            )
            + "\n"
        )
except Exception:
    pass
# #endregion

try:
    settings = Settings()
    # #region agent log
    _log_path = "/home/lucas/hobby/construction/.cursor/debug.log"
    try:
        with open(_log_path, "a") as f:
            f.write(
                json.dumps(
                    {
                        "location": "config.py:53",
                        "message": "Settings created successfully",
                        "data": {"cors_origins": str(settings.CORS_ORIGINS)[:200]},
                        "sessionId": "debug-session",
                        "runId": "startup",
                        "hypothesisId": "SETTINGS_INIT",
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    except Exception:
        pass
    # #endregion
except Exception as e:
    # #region agent log
    _log_path = "/home/lucas/hobby/construction/.cursor/debug.log"
    try:
        with open(_log_path, "a") as f:
            f.write(
                json.dumps(
                    {
                        "location": "config.py:58",
                        "message": "Settings creation failed",
                        "data": {"error_type": type(e).__name__, "error_msg": str(e)},
                        "sessionId": "debug-session",
                        "runId": "startup",
                        "hypothesisId": "SETTINGS_INIT",
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    except Exception:
        pass
    # #endregion
    raise
