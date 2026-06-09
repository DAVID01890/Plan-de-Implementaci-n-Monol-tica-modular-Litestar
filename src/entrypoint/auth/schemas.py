from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LoginRequest:
    email: str
    password: str


@dataclass
class LoginResponse:
    access_token: str
    token_type: str = "Bearer"
