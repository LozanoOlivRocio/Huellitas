from fastapi import APIRouter, Response
from backend.apis.dependencies import ConnectionDep, UserDep
from backend.schemas.huellitas import PetInput, PetOut
from backend.repositories.animales import AnimalRepository
from backend.services.animales import AnimalService
from backend.services.errors import DomainError

router = APIRouter(prefix="/api", tags=["animales"])


@router.get("/animales", response_model=list[PetOut])
def list_animals(connection: ConnectionDep):
    return AnimalRepository(connection).list()


@router.get("/animales/{pet_id}", response_model=PetOut)
def get_animal(pet_id: int, connection: ConnectionDep):
    pet = next(
        (p for p in AnimalRepository(connection).list() if p["id"] == pet_id), None
    )
    if not pet:
        raise DomainError("No encontramos esta mascota.", 404)
    return pet


@router.post("/animales", response_model=PetOut, status_code=201)
def publish(data: PetInput, connection: ConnectionDep, user: UserDep):
    return AnimalService(connection).publish(user["id"], data)


@router.get("/fotos/{photo_id}")
def photo(photo_id: int, connection: ConnectionDep):
    row = AnimalRepository(connection).photo_by_id(photo_id)
    if not row or row["contenido"] is None:
        raise DomainError("No encontramos esta fotografía.", 404)
    return Response(
        bytes(row["contenido"]),
        media_type="image/jpeg",
        headers={
            "Cache-Control": "public, max-age=86400",
            "X-Content-Type-Options": "nosniff",
        },
    )
