from __future__ import annotations

from uuid import UUID

from litestar import Controller, delete, get, post
from litestar.exceptions import HTTPException
from litestar.params import FromPath

from src.entrypoint.scrum.schemas import (
    AddHistoriaToSprintRequest,
    CreateHistoriaRequest,
    CreateProyectoRequest,
    CreateSprintRequest,
    HistoriaResponse,
    ProyectoResponse,
    SprintResponse,
)
from src.scrum.domain.entities import (
    HistoriaDeUsuario,
    HistoriaId,
    Proyecto,
    ProyectoId,
    SprintId,
)
from src.scrum.domain.value_objects import StoryPoint
from src.scrum.ports.proyecto_repository import ProyectoRepository
from src.shared_kernel.domain.base_exceptions import BusinessRuleError, NotFoundError, ValidationError
from src.shared_kernel.domain.base_value_objects import NotEmptyString


def _proyecto_to_response(proyecto: Proyecto) -> ProyectoResponse:
    return ProyectoResponse(
        id=str(proyecto.id),
        nombre=str(proyecto.nombre),
        sprints=[
            SprintResponse(
                id=str(s.id),
                nombre=str(s.nombre),
                status=s.status.value,
                fecha_inicio=s.fecha_inicio.isoformat() if s.fecha_inicio else None,
                fecha_fin=s.fecha_fin.isoformat() if s.fecha_fin else None,
                backlog=[str(h) for h in s.backlog],
            )
            for s in proyecto.sprints
        ],
        historias=[
            HistoriaResponse(
                id=str(h.id),
                titulo=str(h.title),
                descripcion=h.description,
                story_points=h.story_points.value,
                status=h.status.value,
            )
            for h in proyecto.historias
        ],
    )


class ProyectoController(Controller):
    path = "/proyectos"

    @post("/")
    async def create_proyecto(
        self,
        data: CreateProyectoRequest,
        proyecto_repo: ProyectoRepository,
    ) -> ProyectoResponse:
        try:
            proyecto = Proyecto.create(nombre=NotEmptyString(data.nombre))
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        await proyecto_repo.save(proyecto)
        return _proyecto_to_response(proyecto)

    @get("/")
    async def list_proyectos(
        self,
        proyecto_repo: ProyectoRepository,
    ) -> list[ProyectoResponse]:
        proyectos = await proyecto_repo.list()
        return [_proyecto_to_response(p) for p in proyectos]

    @get("/{proyecto_id:str}")
    async def get_proyecto(
        self,
        proyecto_id: FromPath[str],
        proyecto_repo: ProyectoRepository,
    ) -> ProyectoResponse:
        try:
            pid = ProyectoId(UUID(proyecto_id))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid proyecto ID")
        proyecto = await proyecto_repo.find_by_id(pid)
        if proyecto is None:
            raise HTTPException(status_code=404, detail="Proyecto not found")
        return _proyecto_to_response(proyecto)

    @delete("/{proyecto_id:str}", status_code=200)
    async def delete_proyecto(
        self,
        proyecto_id: FromPath[str],
        proyecto_repo: ProyectoRepository,
    ) -> dict[str, str]:
        try:
            pid = ProyectoId(UUID(proyecto_id))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid proyecto ID")
        proyecto = await proyecto_repo.find_by_id(pid)
        if proyecto is None:
            raise HTTPException(status_code=404, detail="Proyecto not found")
        await proyecto_repo.delete(pid)
        return {"status": "deleted"}

    @post("/{proyecto_id:str}/historias")
    async def add_historia(
        self,
        proyecto_id: FromPath[str],
        data: CreateHistoriaRequest,
        proyecto_repo: ProyectoRepository,
    ) -> ProyectoResponse:
        try:
            pid = ProyectoId(UUID(proyecto_id))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid proyecto ID")
        proyecto = await proyecto_repo.find_by_id(pid)
        if proyecto is None:
            raise HTTPException(status_code=404, detail="Proyecto not found")
        try:
            historia = HistoriaDeUsuario(
                title=NotEmptyString(data.titulo),
                story_points=StoryPoint(data.story_points),
                description=data.descripcion,
            )
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        proyecto.add_historia(historia)
        await proyecto_repo.save(proyecto)
        return _proyecto_to_response(proyecto)

    @post("/{proyecto_id:str}/sprints")
    async def create_sprint(
        self,
        proyecto_id: FromPath[str],
        data: CreateSprintRequest,
        proyecto_repo: ProyectoRepository,
    ) -> ProyectoResponse:
        try:
            pid = ProyectoId(UUID(proyecto_id))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid proyecto ID")
        proyecto = await proyecto_repo.find_by_id(pid)
        if proyecto is None:
            raise HTTPException(status_code=404, detail="Proyecto not found")
        try:
            sprint = proyecto.create_sprint(nombre=NotEmptyString(data.nombre))
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        await proyecto_repo.save(proyecto)
        return _proyecto_to_response(proyecto)

    @post("/{proyecto_id:str}/sprints/historias")
    async def add_historia_to_sprint(
        self,
        proyecto_id: FromPath[str],
        data: AddHistoriaToSprintRequest,
        proyecto_repo: ProyectoRepository,
    ) -> ProyectoResponse:
        try:
            pid = ProyectoId(UUID(proyecto_id))
            historia_id = UUID(data.historia_id)
            sprint_id = UUID(data.sprint_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID")
        proyecto = await proyecto_repo.find_by_id(pid)
        if proyecto is None:
            raise HTTPException(status_code=404, detail="Proyecto not found")
        try:
            proyecto.add_historia_to_sprint(HistoriaId(historia_id), SprintId(sprint_id))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except BusinessRuleError as e:
            raise HTTPException(status_code=409, detail=str(e))
        await proyecto_repo.save(proyecto)
        return _proyecto_to_response(proyecto)

    @post("/{proyecto_id:str}/sprints/{sprint_id:str}/start")
    async def start_sprint(
        self,
        proyecto_id: FromPath[str],
        sprint_id: FromPath[str],
        proyecto_repo: ProyectoRepository,
    ) -> ProyectoResponse:
        try:
            pid = ProyectoId(UUID(proyecto_id))
            sid = UUID(sprint_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID")
        proyecto = await proyecto_repo.find_by_id(pid)
        if proyecto is None:
            raise HTTPException(status_code=404, detail="Proyecto not found")
        try:
            proyecto.start_sprint(SprintId(sid))
        except NotFoundError:
            raise HTTPException(status_code=404, detail="Sprint not found")
        except BusinessRuleError as e:
            raise HTTPException(status_code=409, detail=str(e))
        await proyecto_repo.save(proyecto)
        return _proyecto_to_response(proyecto)
