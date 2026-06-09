from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    sqlite_path: str = "local.db"
    turso_url: str = ""
    turso_token: str = ""
    outbox_webhook_url: str = ""
    skip_db_init: bool = False
    debug: bool = False
    auth_provider: str = "internal"
    jwt_secret: str = "CHANGE-ME-IN-PRODUCTION--32bytes!"

    @classmethod
    def from_env(cls, env_file: str | None = None) -> Settings:
        if env_file:
            load_dotenv(env_file)
        return cls(
            sqlite_path=os.getenv("SQLITE_PATH", "local.db"),
            turso_url=os.getenv("TURSO_DATABASE_URL", ""),
            turso_token=os.getenv("TURSO_AUTH_TOKEN", ""),
            outbox_webhook_url=os.getenv("OUTBOX_WEBHOOK_URL", ""),
            skip_db_init=os.getenv("SKIP_DB_INIT") == "1",
            debug=os.getenv("DEBUG") == "1",
            auth_provider=os.getenv("AUTH_PROVIDER", "internal"),
            jwt_secret=os.getenv("JWT_SECRET", "CHANGE-ME-IN-PRODUCTION--32bytes!"),
        )

    @property
    def is_turso_enabled(self) -> bool:
        return bool(self.turso_url and self.turso_token)
