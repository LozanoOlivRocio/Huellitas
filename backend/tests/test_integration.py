import base64
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import pyodbc
from contextlib import contextmanager
from PIL import Image
from fastapi.testclient import TestClient
from backend.main import create_app


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


def register(client, account, email="ana@example.com"):
    response = client.post("/api/auth/register", json={**account, "email": email})
    assert response.status_code == 201, response.text
    return response.json()


def pet_data():
    output = BytesIO()
    Image.new("RGB", (8, 8), "green").save(output, format="PNG")
    return dict(
        nombre="Milo",
        especie="Perro",
        sexo="Macho",
        edad="2 años",
        tamano="Mediano",
        temperamento="Sociable y juguetón",
        historia="Milo busca un hogar responsable donde pueda pasear y recibir cariño todos los días.",
        ubicacion="El Tambo, Junín",
        foto="data:image/png;base64," + base64.b64encode(output.getvalue()).decode(),
        fotos=[],
        vacunado=True,
        desparasitado=True,
        esterilizado=False,
    )


def publish(client):
    response = client.post("/api/animales", json=pet_data())
    assert response.status_code == 201, response.text
    return response.json()


def apply(client, pet_id):
    response = client.post(
        "/api/solicitudes",
        json=dict(
            petId=pet_id,
            vivienda="Casa con jardín",
            otrasMascotas=False,
            ninos=False,
            motivacion="Tenemos tiempo, espacio seguro y recursos para cuidar de nuestro nuevo compañero.",
        ),
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_health_and_authentication(app, account, settings):
    assert app.get("/api/health").json() == {"status": "ok", "database": "sqlserver"}
    assert app.get("/api/auth/me").status_code == 401
    user = register(app, account)
    assert app.get("/api/auth/me").json() == user
    with raw_connection(settings.sqlserver_connection_string) as db:
        password = db.execute(
            "SELECT password_hash FROM adopcion.usuarios WHERE id=?", (user["id"],)
        ).fetchone()[0]
        assert password.startswith("$argon2") and account["password"] not in password
        assert (
            db.execute("SELECT LEN(token_hash) FROM adopcion.sesiones").fetchone()[0]
            == 64
        )
    assert next(
        c for c in app.cookies.jar if c.name == "huellitas_session"
    ).has_nonstandard_attr("HttpOnly")
    cookie = app.cookies.get("huellitas_session")
    assert app.post("/api/auth/logout").status_code == 204
    assert app.get("/api/auth/me").status_code == 401
    app.cookies.set("huellitas_session", cookie, path="/api")
    assert app.get("/api/auth/me").status_code == 401  # revocación en servidor
    assert (
        app.post(
            "/api/auth/login",
            json={"email": account["email"], "password": "incorrecta"},
        ).status_code
        == 401
    )
    assert (
        app.post(
            "/api/auth/login",
            json={"email": account["email"], "password": account["password"]},
        ).status_code
        == 200
    )


def test_server_validation_and_duplicate_email(app, account):
    register(app, account)
    assert (
        app.post(
            "/api/auth/register", json={**account, "email": "ANA@example.com"}
        ).status_code
        == 409
    )
    assert (
        app.post(
            "/api/auth/register",
            json={**account, "email": "otra@example.com", "documento": "12"},
        ).status_code
        == 422
    )
    assert (
        app.post("/api/animales", json={**pet_data(), "historia": "corta"}).status_code
        == 422
    )
    assert (
        app.post(
            "/api/animales",
            json={**pet_data(), "foto": "data:image/png;base64,aW52YWxpZA=="},
        ).status_code
        == 422
    )
    assert (
        app.post("/api/animales", json={**pet_data(), "owner": "999"}).status_code
        == 422
    )


def test_photos_favorites_and_database_persistence(app, account, settings):
    user = register(app, account)
    pet = publish(app)
    image = app.get(pet["foto"])
    assert image.status_code == 200
    assert image.headers["content-type"] == "image/jpeg"
    assert app.put(f"/api/favoritos/{pet['id']}").status_code == 204
    assert app.get("/api/favoritos").json() == [pet["id"]]
    assert app.delete(f"/api/favoritos/{pet['id']}").status_code == 204
    assert app.get("/api/favoritos").json() == []
    with raw_connection(settings.sqlserver_connection_string) as db:
        assert db.execute(
            "SELECT publicador_id FROM adopcion.animales WHERE id=?", (pet["id"],)
        ).fetchone()[0] == int(user["id"])
        assert (
            db.execute(
                "SELECT DATALENGTH(contenido) FROM adopcion.fotos_animal"
            ).fetchone()[0]
            > 0
        )
    with TestClient(create_app(app.app.state.settings)) as restarted:
        assert restarted.get(f"/api/animales/{pet['id']}").json()["nombre"] == "Milo"


def test_permissions_and_chat_between_two_sessions(app, account):
    owner = register(app, account)
    pet = publish(app)
    assert (
        app.post(
            "/api/solicitudes",
            json=dict(
                petId=pet["id"],
                vivienda="Casa con jardín",
                otrasMascotas=False,
                ninos=False,
                motivacion="Un hogar lleno de cariño y paseos diarios para compartir.",
            ),
        ).status_code
        == 403
    )
    with (
        TestClient(create_app(app.app.state.settings)) as adopter,
        TestClient(create_app(app.app.state.settings)) as stranger,
    ):
        user = register(adopter, account, "adoptante@example.com")
        register(stranger, account, "tercero@example.com")
        request = apply(adopter, pet["id"])
        path = f"/api/solicitudes/{request['id']}"
        assert (
            adopter.post(
                "/api/solicitudes",
                json=dict(
                    petId=pet["id"],
                    vivienda="Casa con jardín",
                    otrasMascotas=False,
                    ninos=False,
                    motivacion=request["motivacion"],
                ),
            ).status_code
            == 409
        )
        assert stranger.get(path).status_code == 403
        assert stranger.get("/api/solicitudes").json() == []
        assert (
            stranger.post(
                path + "/mensajes", json={"contenido": "No autorizado"}
            ).status_code
            == 403
        )
        assert adopter.patch(path, json={"estado": "aceptada"}).status_code == 403
        assert (
            adopter.post(
                path + "/mensajes", json={"contenido": "Hola, quisiera conocer a Milo."}
            ).status_code
            == 201
        )
        response = app.post(
            path + "/mensajes", json={"contenido": "Podemos coordinar una visita."}
        )
        assert response.status_code == 201
        messages = adopter.get(path).json()["mensajes"]
        assert [m["sender"] for m in messages] == [user["id"], owner["id"]]
        assert app.patch(path, json={"estado": "cancelada"}).status_code == 403
        assert (
            app.patch(path, json={"estado": "aceptada"}).json()["estado"] == "aceptada"
        )
        assert adopter.get(f"/api/animales/{pet['id']}").json()["estado"] == "adoptado"
        assert adopter.patch(path, json={"estado": "cancelada"}).status_code == 200
        assert app.get(f"/api/animales/{pet['id']}").json()["estado"] == "disponible"
        assert (
            adopter.post(
                path + "/mensajes", json={"contenido": "Después de cancelar"}
            ).status_code
            == 409
        )


def test_acceptance_is_atomic_under_concurrent_requests(app, account, settings):
    register(app, account)
    pet = publish(app)
    with (
        TestClient(create_app(app.app.state.settings)) as first,
        TestClient(create_app(app.app.state.settings)) as second,
    ):
        register(first, account, "uno@example.com")
        register(second, account, "dos@example.com")
        r1 = apply(first, pet["id"])
        r2 = apply(second, pet["id"])

        def accept(request_id):
            with TestClient(create_app(app.app.state.settings)) as independent:
                independent.cookies.update(app.cookies)
                return independent.patch(
                    f"/api/solicitudes/{request_id}", json={"estado": "aceptada"}
                ).status_code

        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(accept, [r1["id"], r2["id"]]))
        assert sorted(statuses) == [200, 409]
        with raw_connection(settings.sqlserver_connection_string) as db:
            states = db.execute(
                "SELECT estado FROM adopcion.solicitudes_adopcion WHERE animal_id=? ORDER BY estado",
                (pet["id"],),
            ).fetchall()
            assert [tuple(row) for row in states] == [("aceptada",), ("rechazada",)]


def test_cross_site_mutations_are_rejected(app, account):
    response = app.post(
        "/api/auth/register",
        json=account,
        headers={"Origin": "https://sitio-ajeno.example"},
    )
    assert response.status_code == 403


def test_session_survives_a_new_client_and_server_pool(app, account):
    register(app, account)
    with TestClient(create_app(app.app.state.settings)) as another_browser_request:
        another_browser_request.cookies.update(app.cookies)
        assert another_browser_request.get("/api/auth/me").status_code == 200


def test_duplicate_submission_race_creates_one_application(app, account, settings):
    register(app, account)
    pet = publish(app)
    with TestClient(create_app(app.app.state.settings)) as adopter:
        register(adopter, account, "adopta@example.com")
        data = dict(
            petId=pet["id"],
            vivienda="Casa con jardín",
            otrasMascotas=False,
            ninos=False,
            motivacion="Podemos compartir tiempo, paseos y un hogar seguro para toda su vida.",
        )

        def submit(_):
            with TestClient(create_app(app.app.state.settings)) as session:
                session.cookies.update(adopter.cookies)
                return session.post("/api/solicitudes", json=data).status_code

        with ThreadPoolExecutor(max_workers=2) as executor:
            assert sorted(executor.map(submit, range(2))) == [201, 409]
