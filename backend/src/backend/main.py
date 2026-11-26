from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pyodbc
from backend.apis import usuarios, animales, solicitudes
from backend.repositories.database import create_pool
from backend.apis.dependencies import ConnectionDep
from backend.services.config import get_settings
from backend.services.errors import DomainError

logger = logging.getLogger(__name__)


def create_app(settings=None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app):
        pool = create_pool(settings.sqlserver_connection_string)
        app.state.pool = pool
        try:
            pool.open(wait=True, timeout=15)
            with pool.connection() as connection:
                if not connection.execute(
                    "SELECT OBJECT_ID(N'adopcion.sesiones',N'U') AS tabla"
                ).fetchone()["tabla"]:
                    raise RuntimeError(
                        "Aplica las migraciones con: uv run huellitas-db"
                    )
            yield
        finally:
            pool.close()

    app = FastAPI(
        title="Huellitas API",
        version="1.0.0",
        lifespan=lifespan,
        description="Adopción responsable con autenticación y SQL Server.",
    )
    app.state.settings = settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
        allow_headers=["Content-Type"],
    )

    @app.middleware("http")
    async def request_safety(request, call_next):
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("origin")
            if origin and origin not in settings.allowed_origins:
                return JSONResponse(
                    {"detail": "Origen de la petición no permitido."}, status_code=403
                )
            if request.headers.get("sec-fetch-site") == "cross-site":
                return JSONResponse(
                    {"detail": "Petición entre sitios no permitida."}, status_code=403
                )
            content_length = request.headers.get("content-length", "0")
            if content_length.isdigit() and int(content_length) > 15_000_000:
                return JSONResponse(
                    {"detail": "El contenido supera el tamaño permitido."},
                    status_code=413,
                )
        response = await call_next(request)
        if not request.url.path.startswith("/api/fotos/"):
            response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.exception_handler(DomainError)
    async def domain_error(request, error):
        return JSONResponse({"detail": error.message}, status_code=error.status)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, error):
        fields = sorted({str(e["loc"][-1]) for e in error.errors()})
        return JSONResponse(
            {
                "detail": "Revisa los campos: "
                + ", ".join(fields)
                + ". Los datos no cumplen el formato requerido."
            },
            status_code=422,
        )

    @app.exception_handler(pyodbc.IntegrityError)
    async def integrity_error(request, error):
        return JSONResponse(
            {
                "detail": "Los datos entran en conflicto con un registro existente o relacionado."
            },
            status_code=409,
        )

    @app.exception_handler(pyodbc.Error)
    async def database_error(request, error):
        # Los interbloqueos y restricciones simultáneas deben poder reintentarse.
        if any(code in str(error) for code in ("(1205)", "(2601)", "(2627)")):
            return JSONResponse(
                {
                    "detail": "Otro proceso modificó estos datos. Actualiza e inténtalo nuevamente."
                },
                status_code=409,
            )
        logger.error("No se pudo completar una operación de SQL Server.")
        return JSONResponse(
            {
                "detail": "No se pudo conectar con la base de datos. Inténtalo nuevamente."
            },
            status_code=503,
        )

    @app.get("/api/health", tags=["estado"])
    def health(connection: ConnectionDep):
        connection.execute("SELECT 1")
        return {"status": "ok", "database": "sqlserver"}

    app.include_router(usuarios.router)
    app.include_router(animales.router)
    app.include_router(solicitudes.router)
    return app


app = create_app()
