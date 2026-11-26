"""Migraciones T-SQL verificadas por checksum, dentro de una transacción."""

import hashlib
import re
from pathlib import Path
from backend.repositories.database import connect
from backend.services.config import get_settings

SQL_DIRECTORY = Path(__file__).resolve().parents[4] / "database" / "sqlserver"


def migrate(connection_string, directory=SQL_DIRECTORY):
    paths = sorted(directory.glob("[0-9][0-9][0-9]_*.sql"))
    if not paths:
        raise RuntimeError("No se encontraron las migraciones de database/sqlserver.")
    with connect(connection_string) as db:
        db.execute("""DECLARE @result int;
            EXEC @result=sys.sp_getapplock @Resource=N'Huellitas.migraciones',
            @LockMode='Exclusive', @LockOwner='Transaction', @LockTimeout=15000;
            IF @result<0 THROW 51000, 'No se pudo bloquear la migración.', 1;""")
        db.execute("""IF OBJECT_ID(N'dbo.huellitas_migrations',N'U') IS NULL
            CREATE TABLE dbo.huellitas_migrations(nombre nvarchar(255) PRIMARY KEY,
            checksum char(64) NOT NULL, aplicada_en datetime2 NOT NULL DEFAULT SYSUTCDATETIME());""")
        for path in paths:
            code = path.read_text(encoding="utf-8-sig")
            checksum = hashlib.sha256(code.encode()).hexdigest()
            previous = db.execute(
                "SELECT checksum FROM dbo.huellitas_migrations WHERE nombre=?",
                (path.name,),
            ).fetchone()
            if previous:
                if previous["checksum"] != checksum:
                    raise RuntimeError(
                        f"La migración aplicada {path.name} fue modificada."
                    )
                continue
            for batch in re.split(
                r"^\s*GO\s*$", code, flags=re.MULTILINE | re.IGNORECASE
            ):
                if batch.strip():
                    db.execute(batch)
            db.execute(
                "INSERT INTO dbo.huellitas_migrations(nombre,checksum) VALUES (?,?)",
                (path.name, checksum),
            )


def main():
    migrate(get_settings().sqlserver_connection_string)
    print("Migraciones de Huellitas aplicadas en SQL Server.")
