from fastapi import APIRouter
from backend.apis.dependencies import ConnectionDep, UserDep
from backend.schemas.huellitas import (
    ApplicationInput,
    ApplicationOut,
    ResolveInput,
    MessageInput,
)
from backend.repositories.solicitudes import SolicitudRepository
from backend.services.solicitudes import SolicitudService

router = APIRouter(prefix="/api/solicitudes", tags=["solicitudes y chat"])


@router.get("", response_model=list[ApplicationOut])
def list_applications(connection: ConnectionDep, user: UserDep):
    return SolicitudRepository(connection).list(user["id"])


@router.post("", response_model=ApplicationOut, status_code=201)
def apply(data: ApplicationInput, connection: ConnectionDep, user: UserDep):
    return SolicitudService(connection).apply(user["id"], data)


@router.get("/{request_id}", response_model=ApplicationOut)
def get_application(request_id: int, connection: ConnectionDep, user: UserDep):
    service = SolicitudService(connection)
    service.accessible(request_id, user["id"])
    return next(r for r in service.repo.list(user["id"]) if r["id"] == str(request_id))


@router.patch("/{request_id}", response_model=ApplicationOut)
def resolve(
    request_id: int, data: ResolveInput, connection: ConnectionDep, user: UserDep
):
    return SolicitudService(connection).resolve(request_id, user["id"], data.estado)


@router.post("/{request_id}/mensajes", response_model=ApplicationOut, status_code=201)
def send(request_id: int, data: MessageInput, connection: ConnectionDep, user: UserDep):
    return SolicitudService(connection).send(request_id, user["id"], data.contenido)
