from __future__ import annotations

from litestar import post
from litestar.exceptions import HTTPException

from src.entrypoint.auth.guards import jwt_auth
from src.entrypoint.auth.schemas import LoginRequest, LoginResponse
from src.idp.domain.entities import Usuario
from src.idp.domain.value_objects import UserRole
from src.idp.ports.usuario_repository import UsuarioRepository
from src.shared_kernel.domain.base_value_objects import Email, NotEmptyString


@post("/auth/login", exclude_from_auth=True)
async def login(
    data: LoginRequest,
    usuario_repo: UsuarioRepository,
) -> LoginResponse:
    try:
        email = Email(data.email)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid email format")
    user = await usuario_repo.find_by_email(email)
    if user is None or not user.verify_password(data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is inactive")
    token = jwt_auth.create_token(identifier=str(user.id))
    return LoginResponse(access_token=token)


@post("/auth/register", exclude_from_auth=True)
async def register(
    data: LoginRequest,
    usuario_repo: UsuarioRepository,
) -> dict[str, str]:
    try:
        email = Email(data.email)
        name = NotEmptyString(data.email.split("@")[0])
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid email")
    existing = await usuario_repo.find_by_email(email)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = Usuario(email=email, name=name, role=UserRole.DEVELOPER)
    user.set_password(data.password)
    await usuario_repo.save(user)
    return {"id": str(user.id), "email": str(user.email)}
