# Base de datos de Huellitas

Motor activo: **SQL Server**. Instancia local: `localhost\SQLEXPRESS`.

- `sqlserver/001_huellitas.sql`: tablas, relaciones e índices.
- `sqlserver/002_retirar_historial_importacion.sql`: retira el registro auxiliar del traslado anterior.
- `sqlserver/consultas.sql`: consultas para abrir en SSMS 22.

Desde `backend/`, con `.env` configurado:

```powershell
uv run huellitas-sqlserver
```

Crea `Huellitas` y `Huellitas_test` si faltan y aplica las migraciones. No elimina
datos ni carga ejemplos. Para aplicar solo migraciones: `uv run huellitas-db`.
Los cambios se registran con checksums en `dbo.huellitas_migrations`; no editar
archivos ya aplicados, sino agregar el siguiente archivo numerado.

En SSMS, conectar con Autenticación de Windows y actualizar **Bases de datos →
Huellitas → Tablas**. Las tablas activas son:

- `adopcion.usuarios`
- `adopcion.animales`
- `adopcion.fotos_animal`
- `adopcion.solicitudes_adopcion`
- `adopcion.mensajes_chat`
- `adopcion.sesiones`
- `adopcion.favoritos`

La base se entrega vacía. Las cuentas y publicaciones nuevas se crean desde la web.
`Huellitas_test` es independiente y se reserva para pruebas automatizadas.
