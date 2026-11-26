-- Abrir en SSMS 22. Solo consultas; no modifica datos.
USE [Huellitas];
GO

SELECT DB_NAME() AS base_actual,
       CONVERT(nvarchar(128), SERVERPROPERTY('ServerName')) AS servidor;

SELECT nombre, aplicada_en AS aplicada_en_utc
FROM dbo.huellitas_migrations ORDER BY nombre;

-- Perfil: excluye hashes de contraseña y tokens.
SELECT id,nombre,apellidos,email,ubicacion,activo,creado_en AS creado_en_utc
FROM adopcion.usuarios ORDER BY id;

SELECT a.id,a.nombre,a.especie,a.estado,a.ubicacion,
       CONCAT_WS(N' ',u.nombre,u.apellidos) AS publicador
FROM adopcion.animales a
JOIN adopcion.usuarios u ON u.id=a.publicador_id
ORDER BY a.id;

SELECT s.id,a.nombre AS mascota,
       CONCAT_WS(N' ',u.nombre,u.apellidos) AS solicitante,
       s.estado,s.creado_en AS fecha_solicitud_utc
FROM adopcion.solicitudes_adopcion s
JOIN adopcion.animales a ON a.id=s.animal_id
JOIN adopcion.usuarios u ON u.id=s.solicitante_id
ORDER BY s.id;

SELECT m.id,m.solicitud_id,CONCAT_WS(N' ',u.nombre,u.apellidos) AS emisor,
       m.contenido,m.fecha_envio AS fecha_envio_utc
FROM adopcion.mensajes_chat m
JOIN adopcion.usuarios u ON u.id=m.emisor_id
ORDER BY m.id;
