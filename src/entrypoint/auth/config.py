from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthSettings:
    secret: str = "CHANGE-ME-IN-PRODUCTION--32bytes!"
    algorithm: str = "HS256"
    expiration_days: int = 7
