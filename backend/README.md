# Backend de Huellitas

FastAPI con SQL Server mediante pyodbc y ODBC Driver 18. Se organiza en `apis`,
`schemas`, `services` y `repositories`.

La configuración se carga de `backend/.env`, usando una ruta independiente del
directorio desde el que se ejecute Python. La plantilla es `.env.example`.

Desde `backend/`:

```powershell
uv sync --python 3.13
uv run huellitas-sqlserver
uv run backend
```

Para iniciar ambos proyectos, ejecutar `../start.cmd`. Las instrucciones detalladas
están en `../COMO_EJECUTAR_HUELLITAS.txt`.

`huellitas-sqlserver` crea las bases si faltan y aplica las migraciones pendientes.
No carga usuarios ni mascotas. `huellitas-db` aplica solamente migraciones.
Las tablas y los checksums de migración se conservan entre arranques.

- API: http://127.0.0.1:8000/docs
- Estado: http://127.0.0.1:8000/api/health
- Base activa: `Huellitas`.
- Base de pruebas: `Huellitas_test`.

```powershell
uv run pytest -q
uv run python tests/smoke_live.py
```

El recorrido HTTP requiere la aplicación iniciada. Usa datos temporales y elimina
solo sus propios registros. Las pruebas automatizadas escriben exclusivamente en
una base cuyo nombre real termina en `_test`.

Las operaciones usan parámetros SQL y transacciones, con rollback ante errores.
Las aceptaciones se protegen mediante bloqueos e índices únicos filtrados. Las
fechas se guardan en UTC; las imágenes normalizadas usan `varbinary(max)`.
