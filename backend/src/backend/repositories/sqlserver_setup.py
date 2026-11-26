"""Preparación local sin borrar bases ni modificar credenciales de Windows."""

import re
import pyodbc
from backend.services.config import get_settings
from backend.repositories.migrations import migrate


def with_database(connection_string, database):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}", database):
        raise ValueError("Nombre de base no válido.")
    pattern = (
        r"(?i)(^|;)\s*(?:DATABASE|Initial Catalog)\s*=\s*(?:\{(?:[^}]|}})*\}|[^;]*)"
    )
    if re.search(pattern, connection_string):
        return re.sub(
            pattern, lambda m: m.group(1) + "DATABASE=" + database, connection_string
        )
    return connection_string.rstrip(";") + ";DATABASE=" + database + ";"


def ensure_database(connection_string, name):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}", name):
        raise ValueError("Nombre de base no válido.")
    admin = pyodbc.connect(
        with_database(connection_string, "master"), autocommit=True, timeout=8
    )
    try:
        # El nombre se valida; los identificadores no admiten parámetros ODBC.
        admin.execute(f"IF DB_ID(N'{name}') IS NULL CREATE DATABASE [{name}]").close()
    finally:
        admin.close()


def main():
    connection_string = get_settings().sqlserver_connection_string
    ensure_database(connection_string, "Huellitas")
    ensure_database(connection_string, "Huellitas_test")
    migrate(connection_string)
    print(
        "Bases Huellitas y Huellitas_test listas en SQL Server. No se borraron datos."
    )
