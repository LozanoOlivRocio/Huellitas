from typing import Annotated
from fastapi import Depends, Request
from backend.repositories.database import Connection, get_connection
from backend.services.usuarios import UsuarioService
from backend.services.errors import DomainError

ConnectionDep = Annotated[Connection, Depends(get_connection, scope="function")]


def current_user(request: Request, connection: ConnectionDep):
    user = UsuarioService(connection).session_user(
        request.cookies.get("huellitas_session")
    )
    if not user:
        raise DomainError("Inicia sesión para continuar.", 401)
    return user


UserDep = Annotated[dict, Depends(current_user, scope="function")]
