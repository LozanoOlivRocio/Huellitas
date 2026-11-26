def application_out(row, messages):
    return dict(
        id=str(row["id"]),
        petId=row["animal_id"],
        userId=str(row["solicitante_id"]),
        nombre=row["nombre"],
        vivienda=row["tipo_vivienda"],
        otrasMascotas=row["tiene_otras_mascotas"],
        ninos=row["tiene_ninos"],
        motivacion=row["motivacion"],
        estado=row["estado"],
        fecha=row["creado_en"],
        mensajes=messages,
    )


class SolicitudRepository:
    def __init__(self, connection):
        self.db = connection

    def get(self, request_id, lock=False):
        return self.db.execute(
            "SELECT * FROM adopcion.solicitudes_adopcion"
            + (" WITH (UPDLOCK,HOLDLOCK)" if lock else "")
            + " WHERE id=?",
            (request_id,),
        ).fetchone()

    def list(self, user_id):
        rows = self.db.execute(
            """SELECT s.*,concat_ws(' ',u.nombre,u.apellidos) nombre
            FROM adopcion.solicitudes_adopcion s JOIN adopcion.animales a ON a.id=s.animal_id
            JOIN adopcion.usuarios u ON u.id=s.solicitante_id
            WHERE s.solicitante_id=? OR a.publicador_id=? ORDER BY s.id DESC""",
            (user_id, user_id),
        ).fetchall()
        messages = {}
        for m in self.db.execute(
            """SELECT m.* FROM adopcion.mensajes_chat m
            JOIN adopcion.solicitudes_adopcion s ON s.id=m.solicitud_id
            JOIN adopcion.animales a ON a.id=s.animal_id
            WHERE s.solicitante_id=? OR a.publicador_id=? ORDER BY m.id""",
            (user_id, user_id),
        ):
            messages.setdefault(m["solicitud_id"], []).append(
                dict(
                    id=str(m["id"]),
                    sender=str(m["emisor_id"]),
                    contenido=m["contenido"],
                    fecha=m["fecha_envio"],
                )
            )
        return [application_out(r, messages.get(r["id"], [])) for r in rows]

    def exists_active(self, pet_id, user_id):
        return (
            self.db.execute(
                "SELECT 1 FROM adopcion.solicitudes_adopcion WHERE animal_id=? AND solicitante_id=? AND estado IN ('pendiente','aceptada')",
                (pet_id, user_id),
            ).fetchone()
            is not None
        )

    def create(self, user_id, data):
        return self.db.execute(
            """INSERT INTO adopcion.solicitudes_adopcion
            (animal_id,solicitante_id,tipo_vivienda,tiene_otras_mascotas,tiene_ninos,motivacion)
            OUTPUT INSERTED.id VALUES (?,?,?,?,?,?)""",
            (
                data.petId,
                user_id,
                data.vivienda,
                data.otrasMascotas,
                data.ninos,
                data.motivacion,
            ),
        ).fetchone()["id"]

    def resolve(self, request_id, status):
        self.db.execute(
            "UPDATE adopcion.solicitudes_adopcion SET estado=?,fecha_resolucion=SYSUTCDATETIME() WHERE id=?",
            (status, request_id),
        )

    def reject_others(self, request_id, pet_id):
        self.db.execute(
            "UPDATE adopcion.solicitudes_adopcion SET estado='rechazada',fecha_resolucion=SYSUTCDATETIME() WHERE animal_id=? AND id<>? AND estado='pendiente'",
            (pet_id, request_id),
        )

    def send(self, request_id, user_id, content):
        self.db.execute(
            "INSERT INTO adopcion.mensajes_chat(solicitud_id,emisor_id,contenido) VALUES (?,?,?)",
            (request_id, user_id, content),
        )
