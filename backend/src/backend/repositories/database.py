"""Conexiones SQL Server: parámetros ODBC, transacciones y resultados por nombre."""

from contextlib import contextmanager
from datetime import datetime, timezone
from threading import BoundedSemaphore
import pyodbc
from fastapi import Request


class Result:
    def __init__(self, cursor):
        self.cursor = cursor
        while cursor.description is None:
            if not cursor.nextset():
                cursor.close()
                self.cursor = None
                break
        self.columns = [c[0] for c in cursor.description] if self.cursor else []

    def _row(self, row):
        if row is None:
            return None
        return {
            name: value.replace(tzinfo=timezone.utc)
            if isinstance(value, datetime) and value.tzinfo is None
            else value
            for name, value in zip(self.columns, row)
        }

    def fetchone(self):
        if self.cursor is None:
            return None
        try:
            return self._row(self.cursor.fetchone())
        finally:
            self.cursor.close()
            self.cursor = None

    def fetchall(self):
        if self.cursor is None:
            return []
        try:
            return [self._row(row) for row in self.cursor.fetchall()]
        finally:
            self.cursor.close()
            self.cursor = None

    def __iter__(self):
        return iter(self.fetchall())


class Connection:
    def __init__(self, raw):
        self.raw = raw

    def execute(self, statement, parameters=()):
        parameters = tuple(
            value.astimezone(timezone.utc).replace(tzinfo=None)
            if isinstance(value, datetime) and value.tzinfo
            else value
            for value in parameters
        )
        cursor = self.raw.cursor()
        try:
            cursor.execute(statement, parameters)
            return Result(cursor)
        except BaseException:
            cursor.close()
            raise


@contextmanager
def connect(connection_string):
    raw = pyodbc.connect(connection_string, timeout=8, autocommit=False)
    try:
        raw.execute(
            "SET NOCOUNT ON; SET XACT_ABORT ON; SET ANSI_NULLS ON; SET QUOTED_IDENTIFIER ON; "
            "SET ANSI_PADDING ON; SET ANSI_WARNINGS ON; SET CONCAT_NULL_YIELDS_NULL ON; "
            "SET ARITHABORT ON; SET NUMERIC_ROUNDABORT OFF;"
        ).close()
        yield Connection(raw)
        raw.commit()
    except BaseException:
        raw.rollback()
        raise
    finally:
        raw.close()


class Database:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.limit = BoundedSemaphore(10)

    def open(self, **_):
        with self.connection() as db:
            db.execute("SELECT 1 AS conectado").fetchone()

    @contextmanager
    def connection(self):
        if not self.limit.acquire(timeout=15):
            raise pyodbc.OperationalError("HYT00", "No hay conexiones disponibles.")
        try:
            with connect(self.connection_string) as db:
                yield db
        finally:
            self.limit.release()

    def close(self):
        # Cada préstamo cierra el handle; ODBC administra la reutilización física.
        pass


def create_pool(connection_string):
    return Database(connection_string)


def get_connection(request: Request):
    with request.app.state.pool.connection() as connection:
        yield connection
