from fastapi import APIRouter, Request, Response
from backend.apis.dependencies import ConnectionDep, UserDep
from backend.repositories.usuarios import user_out, UsuarioRepository
from backend.repositories.animales import AnimalRepository
from backend.schemas.huellitas import Register, Login, UserOut
from backend.services.usuarios import UsuarioService
from backend.services.errors import DomainError

router = APIRouter(prefix="/api", tags=["usuarios"])


def session_response(request, response, service, user):
    old = request.cookies.get("huellitas_session")
    service.logout(old)
    settings = request.app.state.settings
    token, result = service.start_session(user, settings.session_days)
    response.set_cookie(
        "huellitas_session",
        token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.session_days * 86400,
        path="/api",
    )
    response.headers["Cache-Control"] = "no-store"
    return result


@router.post("/auth/register", response_model=UserOut, status_code=201)
def register(
    data: Register, request: Request, response: Response, connection: ConnectionDep
):
    service = UsuarioService(connection)
    return session_response(request, response, service, service.register(data))


@router.post("/auth/login", response_model=UserOut)
def login(data: Login, request: Request, response: Response, connection: ConnectionDep):
    service = UsuarioService(connection)
    return session_response(request, response, service, service.login(data))


@router.post("/auth/logout", status_code=204)
def logout(request: Request, response: Response, connection: ConnectionDep):
    UsuarioService(connection).logout(request.cookies.get("huellitas_session"))
    response.delete_cookie("huellitas_session", path="/api")


@router.get("/auth/me", response_model=UserOut)
def me(user: UserDep):
    return user_out(user)


@router.get("/favoritos", response_model=list[int])
def favorites(connection: ConnectionDep, user: UserDep):
    return UsuarioRepository(connection).favorites(user["id"])


@router.put("/favoritos/{pet_id}", status_code=204)
def favorite(pet_id: int, connection: ConnectionDep, user: UserDep):
    if not AnimalRepository(connection).get(pet_id):
        raise DomainError("No encontramos esta mascota.", 404)
    UsuarioRepository(connection).favorite(user["id"], pet_id, True)


@router.delete("/favoritos/{pet_id}", status_code=204)
def unfavorite(pet_id: int, connection: ConnectionDep, user: UserDep):
    UsuarioRepository(connection).favorite(user["id"], pet_id, False)
