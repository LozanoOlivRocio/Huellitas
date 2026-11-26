# Huellitas

Aplicación de adopción responsable con **Angular, Bootstrap, FastAPI y SQL Server**.

Para iniciar desde esta carpeta:

```powershell
.\start.cmd
```

Web: http://127.0.0.1:4200/. Mantener la consola abierta mientras se utiliza.
Las instrucciones completas están en **COMO_EJECUTAR_HUELLITAS.txt**.

## Estructura

- `frontend/src/app/components/huellitas/`: pantallas y plantillas HTML.
- `frontend/src/app/interfaces/`: contratos de datos.
- `frontend/src/app/services/`: conexión HTTP con FastAPI y estado de Angular.
- `backend/src/backend/apis/`: rutas de la API.
- `backend/src/backend/schemas/`: validación de datos.
- `backend/src/backend/services/`: autenticación y reglas de adopción.
- `backend/src/backend/repositories/`: SQL, conexión y migraciones.
- `database/sqlserver/`: esquema activo y consultas para SSMS.
- `scripts/start.mjs` y `start.cmd`: iniciador de la aplicación.

## Configuración y primer uso

La conexión está en `backend/.env`, excluido de Git. La plantilla es `.env.example`.
Base de aplicación: **Huellitas**. Base separada de pruebas: **Huellitas_test**.
Instancia de esta estación: `localhost\SQLEXPRESS`, con Autenticación de Windows.

El proyecto queda sin usuarios ni publicaciones. El iniciador no carga datos de
ejemplo ni borra registros: la primera cuenta se crea desde la web y las mascotas
se publican desde esa cuenta.

Las dependencias (`node_modules`, `.venv`) se conservan para permitir el arranque.
Las cachés y carpetas de compilación se generan de nuevo cuando sean necesarias.

Registro, sesiones, favoritos, fotografías, solicitudes y chat usan SQL Server.
No hay panel de administrador; una cuenta puede publicar y solicitar mascotas.
El chat se actualiza cada cinco segundos. Las contraseñas usan Argon2 y las
sesiones son revocables mediante cookies HttpOnly.
