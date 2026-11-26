from datetime import datetime, timedelta, timezone


def user_out(row):
    return {
        key: str(row[key]) if key == "id" else row[key] or ""
        for key in (
            "id",
            "nombre",
            "apellidos",
            "email",
            "telefono",
            "documento",
            "ubicacion",
        )
    }


class UsuarioRepository:
    def __init__(self, connection):
        self.db = connection

    def by_email(self, email):
        return self.db.execute(
            "SELECT * FROM adopcion.usuarios WHERE lower(email)=lower(?)", (email,)
        ).fetchone()

    def create(self, data, password_hash):
        return self.db.execute(
            """INSERT INTO adopcion.usuarios
            (nombre,apellidos,email,telefono,documento,ubicacion,password_hash)
            OUTPUT INSERTED.* VALUES (?,?,?,?,?,?,?)""",
            (
                data.nombre,
                data.apellidos,
                str(data.email).lower(),
                data.telefono,
                data.documento,
                data.ubicacion,
                password_hash,
            ),
        ).fetchone()

    def session(self, token_hash):
        return self.db.execute(
            """SELECT u.* FROM adopcion.sesiones s JOIN adopcion.usuarios u
            ON u.id=s.usuario_id WHERE s.token_hash=? AND s.expira_en>SYSUTCDATETIME() AND u.activo=1""",
            (token_hash,),
        ).fetchone()

    def create_session(self, user_id, token_hash, days):
        self.db.execute(
            "DELETE FROM adopcion.sesiones WHERE expira_en<=SYSUTCDATETIME()"
        )
        self.db.execute(
            "INSERT INTO adopcion.sesiones(token_hash,usuario_id,expira_en) VALUES (?,?,?)",
            (token_hash, user_id, datetime.now(timezone.utc) + timedelta(days=days)),
        )

    def delete_session(self, token_hash):
        self.db.execute(
            "DELETE FROM adopcion.sesiones WHERE token_hash=?", (token_hash,)
        )

    def favorites(self, user_id):
        return [
            row["animal_id"]
            for row in self.db.execute(
                "SELECT animal_id FROM adopcion.favoritos WHERE usuario_id=? ORDER BY animal_id",
                (user_id,),
            )
        ]

    def favorite(self, user_id, pet_id, enabled):
        if enabled:
            self.db.execute(
                """IF NOT EXISTS (SELECT 1 FROM adopcion.favoritos WITH (UPDLOCK,HOLDLOCK)
                WHERE usuario_id=? AND animal_id=?)
                INSERT INTO adopcion.favoritos(usuario_id,animal_id) VALUES (?,?)""",
                (user_id, pet_id, user_id, pet_id),
            )
        else:
            self.db.execute(
                "DELETE FROM adopcion.favoritos WHERE usuario_id=? AND animal_id=?",
                (user_id, pet_id),
            )
