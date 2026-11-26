def pet_out(row, photos):
    return dict(
        id=row["id"],
        owner=str(row["publicador_id"]),
        publicador=row["publicador"],
        nombre=row["nombre"],
        especie=row["especie"],
        sexo=row["sexo"].capitalize(),
        edad=row["edad_aproximada"],
        tamano=row["tamano"],
        temperamento=row["temperamento"],
        historia=row["historia"],
        ubicacion=row["ubicacion"],
        foto=photos[0] if photos else "",
        fotos=photos[1:],
        vacunado=row["vacunado"],
        desparasitado=row["desparasitado"],
        esterilizado=row["esterilizado"],
        estado={"adoptada": "adoptado", "retirada": "retirado"}.get(
            row["estado"], row["estado"]
        ),
    )


class AnimalRepository:
    def __init__(self, connection):
        self.db = connection

    def list(self):
        rows = self.db.execute("""SELECT a.*, concat_ws(' ',u.nombre,u.apellidos) publicador
            FROM adopcion.animales a JOIN adopcion.usuarios u ON u.id=a.publicador_id ORDER BY a.id DESC""").fetchall()
        photos = {}
        for photo in self.db.execute(
            "SELECT id,animal_id,url FROM adopcion.fotos_animal ORDER BY animal_id,orden"
        ):
            photos.setdefault(photo["animal_id"], []).append(
                photo["url"] or f"/api/fotos/{photo['id']}"
            )
        return [pet_out(row, photos.get(row["id"], [])) for row in rows]

    def get(self, pet_id, lock=False):
        return self.db.execute(
            "SELECT * FROM adopcion.animales"
            + (" WITH (UPDLOCK,HOLDLOCK)" if lock else "")
            + " WHERE id=?",
            (pet_id,),
        ).fetchone()

    def create(self, owner, data):
        row = self.db.execute(
            """INSERT INTO adopcion.animales
            (publicador_id,nombre,especie,sexo,edad_aproximada,tamano,temperamento,historia,ubicacion,vacunado,desparasitado,esterilizado)
            OUTPUT INSERTED.id VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                owner,
                data.nombre,
                data.especie,
                data.sexo.lower(),
                data.edad,
                data.tamano,
                data.temperamento,
                data.historia,
                data.ubicacion,
                data.vacunado,
                data.desparasitado,
                data.esterilizado,
            ),
        ).fetchone()
        return row["id"]

    def photo(self, pet_id, order, content):
        self.db.execute(
            "INSERT INTO adopcion.fotos_animal(animal_id,orden,contenido) VALUES (?,?,?)",
            (pet_id, order, content),
        )

    def photo_by_id(self, photo_id):
        return self.db.execute(
            "SELECT contenido FROM adopcion.fotos_animal WHERE id=?", (photo_id,)
        ).fetchone()

    def set_status(self, pet_id, status):
        self.db.execute(
            "UPDATE adopcion.animales SET estado=? WHERE id=?", (status, pet_id)
        )
