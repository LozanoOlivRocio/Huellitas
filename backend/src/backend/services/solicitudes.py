from backend.repositories.animales import AnimalRepository
from backend.repositories.solicitudes import SolicitudRepository
from backend.services.errors import DomainError


class SolicitudService:
    def __init__(self, connection):
        self.repo = SolicitudRepository(connection)
        self.animals = AnimalRepository(connection)

    def apply(self, user_id, data):
        pet = self.animals.get(data.petId, lock=True)
        if not pet:
            raise DomainError("No encontramos esta mascota.", 404)
        if pet["publicador_id"] == user_id:
            raise DomainError("No puedes solicitar tu propia mascota.", 403)
        if pet["estado"] != "disponible":
            raise DomainError("Esta mascota ya no está disponible.", 409)
        if self.repo.exists_active(data.petId, user_id):
            raise DomainError("Ya tienes una solicitud activa para esta mascota.", 409)
        request_id = self.repo.create(user_id, data)
        return next(r for r in self.repo.list(user_id) if r["id"] == str(request_id))

    def accessible(self, request_id, user_id, lock=False):
        initial = self.repo.get(request_id)
        if not initial:
            raise DomainError("No encontramos esta solicitud.", 404)
        # Todas las escrituras bloquean primero al animal y después a la solicitud.
        # Esto serializa aceptaciones, cancelaciones y nuevas postulaciones.
        pet = self.animals.get(initial["animal_id"], lock=lock)
        row = self.repo.get(request_id, lock=lock) if lock else initial
        if user_id not in {pet["publicador_id"], row["solicitante_id"]}:
            raise DomainError("No tienes permiso para acceder a esta solicitud.", 403)
        return row, pet

    def resolve(self, request_id, user_id, status):
        row, pet = self.accessible(request_id, user_id, lock=True)
        if row["estado"] not in {"pendiente", "aceptada"}:
            raise DomainError("Esta solicitud ya finalizó.", 409)
        if status == "cancelada":
            if row["solicitante_id"] != user_id:
                raise DomainError(
                    "Solo el solicitante puede cancelar su solicitud.", 403
                )
        elif pet["publicador_id"] != user_id:
            raise DomainError("Solo el publicador puede resolver la solicitud.", 403)
        elif row["estado"] != "pendiente":
            raise DomainError("Solo se puede resolver una solicitud pendiente.", 409)
        if status == "aceptada":
            if pet["estado"] != "disponible":
                raise DomainError("Esta mascota ya no está disponible.", 409)
            self.animals.set_status(pet["id"], "adoptada")
            self.repo.reject_others(request_id, pet["id"])
        elif status == "cancelada" and row["estado"] == "aceptada":
            self.animals.set_status(pet["id"], "disponible")
        self.repo.resolve(request_id, status)
        return next(r for r in self.repo.list(user_id) if r["id"] == str(request_id))

    def send(self, request_id, user_id, content):
        row, _ = self.accessible(request_id, user_id, lock=True)
        if row["estado"] not in {"pendiente", "aceptada"}:
            raise DomainError("Esta conversación está cerrada.", 409)
        self.repo.send(request_id, user_id, content)
        return next(r for r in self.repo.list(user_id) if r["id"] == str(request_id))
