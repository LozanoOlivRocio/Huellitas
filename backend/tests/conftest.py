import os
from backend.repositories.database import connect
from backend.repositories.sqlserver_setup import with_database
import pytest
from fastapi.testclient import TestClient
from backend.main import create_app
from backend.repositories.migrations import migrate
from backend.services.config import get_settings


@pytest.fixture(scope="session")
def settings():
    config = get_settings()
    connection_string = os.environ.get(
        "TEST_SQLSERVER_CONNECTION_STRING"
    ) or with_database(config.sqlserver_connection_string, "Huellitas_test")
    with connect(connection_string) as db:
        name = db.execute("SELECT DB_NAME() AS nombre").fetchone()["nombre"]
        if not name.lower().endswith("_test"):
            raise RuntimeError(
                "Las pruebas solo se ejecutan sobre una base terminada en _test."
            )
    config.sqlserver_connection_string = connection_string
    migrate(connection_string)
    return config


@pytest.fixture
def app(settings):
    with connect(settings.sqlserver_connection_string) as db:
        for table in [
            "favoritos",
            "mensajes_chat",
            "sesiones",
            "solicitudes_adopcion",
            "fotos_animal",
            "animales",
            "usuarios",
        ]:
            db.execute(f"DELETE FROM adopcion.{table}")
    with TestClient(create_app(settings)) as client:
        yield client


@pytest.fixture
def account():
    return dict(
        nombre="Ana",
        apellidos="Prueba",
        email="ana@example.com",
        telefono="+51 999999999",
        documento="12345678",
        ubicacion="Huancayo, Junín",
        password="Prueba-segura-2026!",
    )
