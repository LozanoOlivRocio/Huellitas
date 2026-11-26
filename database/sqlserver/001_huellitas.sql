-- SQL Server / T-SQL. Ejecutar en la base Huellitas mediante huellitas-db.
IF SCHEMA_ID(N'adopcion') IS NULL EXEC(N'CREATE SCHEMA adopcion');
GO

CREATE TABLE adopcion.usuarios (
    id bigint IDENTITY(1,1) PRIMARY KEY,
    nombre nvarchar(100) NOT NULL CHECK(LEN(LTRIM(RTRIM(nombre))) > 0),
    apellidos nvarchar(100) NOT NULL DEFAULT N'',
    email nvarchar(254) COLLATE Latin1_General_100_CI_AS_SC NOT NULL UNIQUE,
    password_hash varchar(512) NOT NULL,
    telefono nvarchar(30),
    documento varchar(8),
    ubicacion nvarchar(200) NOT NULL DEFAULT N'',
    activo bit NOT NULL DEFAULT 1,
    verificado bit NOT NULL DEFAULT 0,
    creado_en datetime2(6) NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT usuarios_dni CHECK(documento IS NULL OR (LEN(documento)=8 AND documento NOT LIKE '%[^0-9]%'))
);

CREATE TABLE adopcion.animales (
    id bigint IDENTITY(1,1) PRIMARY KEY,
    publicador_id bigint NOT NULL REFERENCES adopcion.usuarios(id),
    nombre nvarchar(100) NOT NULL CHECK(LEN(LTRIM(RTRIM(nombre)))>0),
    especie nvarchar(80) NOT NULL,
    sexo nvarchar(15) NOT NULL DEFAULT N'desconocido' CHECK(sexo IN (N'macho',N'hembra',N'desconocido')),
    edad_aproximada nvarchar(40) NOT NULL,
    tamano nvarchar(20) NOT NULL,
    temperamento nvarchar(200) NOT NULL,
    historia nvarchar(4000) NOT NULL CHECK(LEN(LTRIM(RTRIM(historia)))>0),
    ubicacion nvarchar(200) NOT NULL,
    vacunado bit NOT NULL DEFAULT 0,
    desparasitado bit NOT NULL DEFAULT 0,
    esterilizado bit NOT NULL DEFAULT 0,
    estado varchar(20) NOT NULL DEFAULT 'disponible' CHECK(estado IN ('disponible','adoptada','retirada')),
    creado_en datetime2(6) NOT NULL DEFAULT SYSUTCDATETIME()
);
CREATE INDEX animales_publicador_idx ON adopcion.animales(publicador_id);
CREATE INDEX animales_estado_especie_idx ON adopcion.animales(estado,especie);

CREATE TABLE adopcion.fotos_animal (
    id bigint IDENTITY(1,1) PRIMARY KEY,
    animal_id bigint NOT NULL REFERENCES adopcion.animales(id) ON DELETE CASCADE,
    orden smallint NOT NULL CHECK(orden BETWEEN 0 AND 4),
    contenido varbinary(max),
    url nvarchar(2048),
    CONSTRAINT foto_origen CHECK((contenido IS NOT NULL AND url IS NULL) OR (contenido IS NULL AND url IS NOT NULL)),
    CONSTRAINT foto_orden UNIQUE(animal_id,orden)
);

CREATE TABLE adopcion.solicitudes_adopcion (
    id bigint IDENTITY(1,1) PRIMARY KEY,
    animal_id bigint NOT NULL REFERENCES adopcion.animales(id),
    solicitante_id bigint NOT NULL REFERENCES adopcion.usuarios(id),
    tipo_vivienda nvarchar(100) NOT NULL,
    tiene_otras_mascotas bit NOT NULL DEFAULT 0,
    tiene_ninos bit NOT NULL DEFAULT 0,
    motivacion nvarchar(2000) NOT NULL CHECK(LEN(LTRIM(RTRIM(motivacion)))>0),
    estado varchar(20) NOT NULL DEFAULT 'pendiente' CHECK(estado IN ('pendiente','aceptada','rechazada','cancelada')),
    creado_en datetime2(6) NOT NULL DEFAULT SYSUTCDATETIME(),
    fecha_resolucion datetime2(6)
);
CREATE UNIQUE INDEX solicitud_aceptada_por_animal ON adopcion.solicitudes_adopcion(animal_id) WHERE estado='aceptada';
CREATE UNIQUE INDEX solicitud_activa_unica ON adopcion.solicitudes_adopcion(animal_id,solicitante_id) WHERE estado IN ('pendiente','aceptada');
CREATE INDEX solicitudes_solicitante_idx ON adopcion.solicitudes_adopcion(solicitante_id);

CREATE TABLE adopcion.mensajes_chat (
    id bigint IDENTITY(1,1) PRIMARY KEY,
    solicitud_id bigint NOT NULL REFERENCES adopcion.solicitudes_adopcion(id),
    emisor_id bigint NOT NULL REFERENCES adopcion.usuarios(id),
    contenido nvarchar(2000) NOT NULL CHECK(LEN(LTRIM(RTRIM(contenido)))>0),
    fecha_envio datetime2(6) NOT NULL DEFAULT SYSUTCDATETIME(),
    fecha_lectura datetime2(6)
);
CREATE INDEX mensajes_solicitud_idx ON adopcion.mensajes_chat(solicitud_id,id);

CREATE TABLE adopcion.sesiones (
    token_hash char(64) PRIMARY KEY,
    usuario_id bigint NOT NULL REFERENCES adopcion.usuarios(id) ON DELETE CASCADE,
    expira_en datetime2(6) NOT NULL
);
CREATE INDEX sesiones_usuario_idx ON adopcion.sesiones(usuario_id);

CREATE TABLE adopcion.favoritos (
    usuario_id bigint NOT NULL REFERENCES adopcion.usuarios(id) ON DELETE CASCADE,
    animal_id bigint NOT NULL REFERENCES adopcion.animales(id) ON DELETE CASCADE,
    PRIMARY KEY(usuario_id,animal_id)
);
