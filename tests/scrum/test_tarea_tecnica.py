import pytest

from src.scrum.domain.entities import (
    HistoriaDeUsuario,
    HistoriaId,
    TareaTecnica,
    TareaTecnicaId,
    TareaTecnicaStatus,
)
from src.scrum.domain.value_objects import HorasEstimadas, StoryPoint
from src.shared_kernel.domain.base_exceptions import BusinessRuleError
from src.shared_kernel.domain.base_value_objects import NotEmptyString


@pytest.fixture
def historia() -> HistoriaDeUsuario:
    return HistoriaDeUsuario(
        title=NotEmptyString("Login feature"),
        story_points=StoryPoint(8),
    )


class TestTareaTecnicaCreation:
    def test_create_with_required_fields(self, historia: HistoriaDeUsuario) -> None:
        t = TareaTecnica(
            historia_id=historia.id,
            title=NotEmptyString("Implement login form"),
            estimated_hours=HorasEstimadas(8),
        )
        assert isinstance(t.id, TareaTecnicaId)
        assert t.historia_id == historia.id
        assert t.title == NotEmptyString("Implement login form")
        assert t.estimated_hours == HorasEstimadas(8)
        assert t.description is None
        assert t.status == TareaTecnicaStatus.PENDING

    def test_create_with_description(self, historia: HistoriaDeUsuario) -> None:
        t = TareaTecnica(
            historia_id=historia.id,
            title=NotEmptyString("Add validation"),
            estimated_hours=HorasEstimadas(4),
            description="Client-side and server-side validation",
        )
        assert t.description == "Client-side and server-side validation"

    def test_create_with_explicit_status(self, historia: HistoriaDeUsuario) -> None:
        t = TareaTecnica(
            historia_id=historia.id,
            title=NotEmptyString("Done task"),
            estimated_hours=HorasEstimadas(2),
            status=TareaTecnicaStatus.DONE,
        )
        assert t.status == TareaTecnicaStatus.DONE

    def test_create_with_explicit_id(self, historia: HistoriaDeUsuario) -> None:
        tid = TareaTecnicaId()
        t = TareaTecnica(
            id=tid,
            historia_id=historia.id,
            title=NotEmptyString("Test"),
            estimated_hours=HorasEstimadas(1),
        )
        assert t.id == tid


class TestTareaTecnicaWorkflow:
    def test_start_work(self, historia: HistoriaDeUsuario) -> None:
        t = TareaTecnica(
            historia_id=historia.id,
            title=NotEmptyString("Backend API"),
            estimated_hours=HorasEstimadas(16),
        )
        t.start_work()
        assert t.status == TareaTecnicaStatus.IN_PROGRESS

    def test_complete(self, historia: HistoriaDeUsuario) -> None:
        t = TareaTecnica(
            historia_id=historia.id,
            title=NotEmptyString("Backend API"),
            estimated_hours=HorasEstimadas(16),
        )
        t.start_work()
        t.complete()
        assert t.status == TareaTecnicaStatus.DONE


class TestTareaTecnicaWorkflowErrors:
    def test_start_work_from_in_progress_raises_error(
        self, historia: HistoriaDeUsuario
    ) -> None:
        t = TareaTecnica(
            historia_id=historia.id,
            title=NotEmptyString("Task"),
            estimated_hours=HorasEstimadas(4),
        )
        t.start_work()
        with pytest.raises(BusinessRuleError, match="in_progress"):
            t.start_work()

    def test_complete_from_pending_raises_error(
        self, historia: HistoriaDeUsuario
    ) -> None:
        t = TareaTecnica(
            historia_id=historia.id,
            title=NotEmptyString("Task"),
            estimated_hours=HorasEstimadas(4),
        )
        with pytest.raises(BusinessRuleError, match="pending"):
            t.complete()

    def test_complete_from_done_raises_error(
        self, historia: HistoriaDeUsuario
    ) -> None:
        t = TareaTecnica(
            historia_id=historia.id,
            title=NotEmptyString("Task"),
            estimated_hours=HorasEstimadas(4),
        )
        t.start_work()
        t.complete()
        with pytest.raises(BusinessRuleError, match="done"):
            t.complete()


class TestTareaTecnicaEquality:
    def test_equality_by_id(self, historia: HistoriaDeUsuario) -> None:
        tid = TareaTecnicaId()
        t1 = TareaTecnica(
            id=tid,
            historia_id=historia.id,
            title=NotEmptyString("A"),
            estimated_hours=HorasEstimadas(2),
        )
        t2 = TareaTecnica(
            id=tid,
            historia_id=historia.id,
            title=NotEmptyString("B"),
            estimated_hours=HorasEstimadas(4),
        )
        assert t1 == t2

    def test_inequality(self, historia: HistoriaDeUsuario) -> None:
        t1 = TareaTecnica(
            historia_id=historia.id,
            title=NotEmptyString("A"),
            estimated_hours=HorasEstimadas(2),
        )
        t2 = TareaTecnica(
            historia_id=historia.id,
            title=NotEmptyString("B"),
            estimated_hours=HorasEstimadas(4),
        )
        assert t1 != t2

    def test_hash(self, historia: HistoriaDeUsuario) -> None:
        tid = TareaTecnicaId()
        t1 = TareaTecnica(
            id=tid,
            historia_id=historia.id,
            title=NotEmptyString("A"),
            estimated_hours=HorasEstimadas(2),
        )
        t2 = TareaTecnica(
            id=tid,
            historia_id=historia.id,
            title=NotEmptyString("B"),
            estimated_hours=HorasEstimadas(4),
        )
        assert hash(t1) == hash(t2)


class TestTareaTecnicaStr:
    def test_str(self, historia: HistoriaDeUsuario) -> None:
        t = TareaTecnica(
            historia_id=historia.id,
            title=NotEmptyString("Write tests"),
            estimated_hours=HorasEstimadas(3),
        )
        assert str(t).startswith("TareaTecnica(")

    def test_repr(self, historia: HistoriaDeUsuario) -> None:
        t = TareaTecnica(
            historia_id=historia.id,
            title=NotEmptyString("Write tests"),
            estimated_hours=HorasEstimadas(3),
        )
        assert repr(t).startswith("TareaTecnica(id=")
        assert "historia_id=" in repr(t)
