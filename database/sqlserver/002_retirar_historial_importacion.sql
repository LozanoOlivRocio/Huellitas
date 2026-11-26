-- El traslado de PostgreSQL finalizó; ya no se utiliza este registro auxiliar.
IF OBJECT_ID(N'dbo.huellitas_importaciones',N'U') IS NOT NULL
    DROP TABLE dbo.huellitas_importaciones;
