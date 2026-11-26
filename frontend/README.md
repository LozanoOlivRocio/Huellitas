# Frontend de Huellitas

Angular con componentes independientes, Signals, formularios y **Bootstrap 5.3.3
instalado con npm**, sin CDN de Bootstrap. Se utilizan su rejilla responsive,
tarjetas, botones, controles de formulario, alertas y utilidades. El estilo propio
mantiene el verde, amarillo y menta de las referencias.

## Organización

- `src/app/components/huellitas/`: pantallas y plantillas HTML separadas.
- `src/app/interfaces/huellitas.interface.ts`: contratos del frontend y la API.
- `src/app/services/huellitas.service.ts`: peticiones HTTP y estado compartido.
- `src/styles*.css`: estilos base, pantallas y adaptación responsive.
- `proxy.conf.json`: reenvía `/api/**` hacia FastAPI en desarrollo.
- `src/server.ts`: mismo proxy para la compilación Angular/Express.

## Iniciar

Para levantar toda la aplicación en Windows, usar `../start.cmd`. Para iniciar solo Angular,
con FastAPI ya disponible en el puerto 8000:

```powershell
npm ci
npm start
```

`start.cmd` localiza Node portátil sin requerir cambios de política.
Las instrucciones completas están en `../COMO_EJECUTAR_HUELLITAS.txt`.
Web: http://127.0.0.1:4200/. Usar el mismo hostname durante el flujo para conservar
la cookie de sesión; `localhost` y `127.0.0.1` son hosts diferentes.

## Pantallas

| Ruta | Función |
| --- | --- |
| `/` | Catálogo, búsqueda, especies y favoritos |
| `/login` | Inicio de sesión con FastAPI |
| `/crear-cuenta` | Registro persistente |
| `/mascotas/:id` | Fotos, historia, salud y publicador |
| `/adoptar/:id` | Solicitud de adopción |
| `/publicar` | Registro con fotos |
| `/mi-perfil` | Publicaciones y solicitudes enviadas/recibidas |
| `/mensajes` y `/mensajes/:id` | Chat y estado de solicitud |

El catálogo se consulta sin sesión. Publicar, guardar favoritos, solicitar y
conversar requiere autenticación. La API comprueba todos los permisos.
No se guardan cuentas, contraseñas ni mensajes en el almacenamiento del navegador;
las sesiones usan cookies HttpOnly. El chat consulta las novedades cada cinco
segundos y funciona entre navegadores/dispositivos que accedan al mismo servidor.

## Validar y compilar

```powershell
npm test -- --watch=false
npm run build
npm run serve:ssr:frontend
```

El servidor compilado usa el puerto 4000 y reenvía `/api` a
`API_URL` o, por defecto, `http://127.0.0.1:8000`.

Las pruebas verifican la comunicación HTTP, la recuperación de sesión, los errores
del servidor y la identidad visual. La revisión en Chrome comprobó el catálogo y
los controles de Bootstrap en escritorio/tablet y una vista móvil de 420 px.

Las fuentes e imágenes iniciales requieren internet. Las fotografías publicadas
por usuarios se sirven desde FastAPI y SQL Server. La URL `/api/health` informa
`"database": "sqlserver"` cuando la conexión está disponible.
