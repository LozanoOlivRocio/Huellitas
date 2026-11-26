"""Verificación HTTP del frontend → proxy → API → PostgreSQL. Usa solo datos ficticios."""

import argparse
import base64
from io import BytesIO
import secrets
import uuid
import httpx
import pyodbc
from contextlib import contextmanager
from PIL import Image
from backend.services.config import get_settings


@contextmanager
def raw_connection(connection_string):
    db = pyodbc.connect(connection_string)
    try:
        yield db
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:4200")
    args = parser.parse_args()
    marker = uuid.uuid4().hex
    emails = [f"verificacion.{marker}.{i}@example.com" for i in range(2)]
    password = secrets.token_urlsafe(24)
    headers = {"Origin": args.url}
    with (
        httpx.Client(base_url=args.url, headers=headers, timeout=30) as owner,
        httpx.Client(base_url=args.url, headers=headers, timeout=30) as adopter,
    ):
        try:
            assert owner.get("/api/health").json()["database"] == "sqlserver"
            data = dict(
                nombre="Prueba",
                apellidos="Funcional",
                telefono="999999999",
                documento="12345678",
                ubicacion="Huancayo",
                password=password,
            )
            for client, email in zip([owner, adopter], emails):
                response = client.post(
                    "/api/auth/register", json={**data, "email": email}
                )
                assert response.status_code == 201, response.text
            image = BytesIO()
            Image.new("RGB", (20, 20), "green").save(image, format="PNG")
            response = owner.post(
                "/api/animales",
                json=dict(
                    nombre="Mascota de verificación",
                    especie="Perro",
                    sexo="Macho",
                    edad="2 años",
                    tamano="Mediano",
                    temperamento="Tranquilo",
                    historia="Publicación temporal para comprobar que el flujo completo guarda los datos correctamente.",
                    ubicacion="Huancayo",
                    foto="data:image/png;base64,"
                    + base64.b64encode(image.getvalue()).decode(),
                    fotos=[],
                    vacunado=True,
                    desparasitado=True,
                    esterilizado=True,
                ),
            )
            assert response.status_code == 201, response.text
            pet = response.json()
            assert adopter.get(pet["foto"]).status_code == 200
            response = adopter.post(
                "/api/solicitudes",
                json=dict(
                    petId=pet["id"],
                    vivienda="Casa con jardín",
                    otrasMascotas=False,
                    ninos=False,
                    motivacion="Contamos con tiempo, espacio y recursos para una adopción responsable.",
                ),
            )
            assert response.status_code == 201, response.text
            path = "/api/solicitudes/" + response.json()["id"]
            assert (
                adopter.post(
                    path + "/mensajes", json={"contenido": "Hola, quisiera conocerlo."}
                ).status_code
                == 201
            )
            assert (
                owner.get(path).json()["mensajes"][0]["contenido"]
                == "Hola, quisiera conocerlo."
            )
            assert (
                owner.post(
                    path + "/mensajes", json={"contenido": "Gracias por escribir."}
                ).status_code
                == 201
            )
            assert len(adopter.get(path).json()["mensajes"]) == 2
            assert owner.patch(path, json={"estado": "aceptada"}).status_code == 200
            assert (
                adopter.get("/api/animales/" + str(pet["id"])).json()["estado"]
                == "adoptado"
            )
            assert adopter.post("/api/auth/logout").status_code == 204
            assert adopter.get("/api/auth/me").status_code == 401
            assert (
                adopter.post(
                    "/api/auth/login", json={"email": emails[1], "password": password}
                ).status_code
                == 200
            )
            assert adopter.get(path).json()["estado"] == "aceptada"
            with raw_connection(get_settings().sqlserver_connection_string) as db:
                assert (
                    db.execute(
                        "SELECT count(*) FROM adopcion.mensajes_chat m JOIN adopcion.solicitudes_adopcion s ON s.id=m.solicitud_id WHERE s.animal_id=?",
                        (pet["id"],),
                    ).fetchone()[0]
                    == 2
                )
            print(
                "OK: registro, cookies, fotos, publicación, solicitud, chat entre sesiones, aceptación, logout, login y persistencia a través del proxy."
            )
        finally:
            # Solo elimina los registros creados por esta ejecución con UUID exclusivo.
            with raw_connection(get_settings().sqlserver_connection_string) as db:
                ids = [
                    r[0]
                    for r in db.execute(
                        "SELECT id FROM adopcion.usuarios WHERE email IN (?,?)",
                        tuple(emails),
                    )
                ]
                if ids:
                    placeholders = ",".join("?" for _ in ids)
                    db.execute(
                        f"DELETE FROM adopcion.mensajes_chat WHERE emisor_id IN ({placeholders})",
                        tuple(ids),
                    )
                    db.execute(
                        f"DELETE FROM adopcion.solicitudes_adopcion WHERE solicitante_id IN ({placeholders}) OR animal_id IN (SELECT id FROM adopcion.animales WHERE publicador_id IN ({placeholders}))",
                        tuple(ids + ids),
                    )
                    db.execute(
                        f"DELETE FROM adopcion.animales WHERE publicador_id IN ({placeholders})",
                        tuple(ids),
                    )
                    db.execute(
                        f"DELETE FROM adopcion.usuarios WHERE id IN ({placeholders})",
                        tuple(ids),
                    )


if __name__ == "__main__":
    main()
