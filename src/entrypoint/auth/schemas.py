from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LoginRequest:
    email: str
    password: str


@dataclass
class RegisterRequest:
    name: str
    email: str
    password: str


@dataclass
class UserResponse:
    id: str
    email: str
    name: str
    role: str


@dataclass
class LoginResponse:
    access_token: str
    user: UserResponse | None = None
    token_type: str = "Bearer"
