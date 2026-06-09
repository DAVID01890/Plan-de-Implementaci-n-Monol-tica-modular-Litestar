from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class AuthSettings:
    secret: str = "CHANGE-ME-IN-PRODUCTION--32bytes!"
    algorithm: str = "HS256"
    expiration_days: int = 7

    @classmethod
    def from_env(cls, env_file: str | None = None) -> AuthSettings:
        if env_file:
            load_dotenv(env_file)
        return cls(
            secret=os.getenv("JWT_SECRET", "CHANGE-ME-IN-PRODUCTION--32bytes!"),
            algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        )
