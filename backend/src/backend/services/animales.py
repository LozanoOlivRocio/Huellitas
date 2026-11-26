import base64
import binascii
import io
from PIL import Image, ImageOps, UnidentifiedImageError
from backend.repositories.animales import AnimalRepository
from backend.services.errors import DomainError


def image_bytes(value: str) -> bytes:
    try:
        header, encoded = value.split(",", 1)
        if header not in {
            "data:image/jpeg;base64",
            "data:image/png;base64",
            "data:image/webp;base64",
        }:
            raise ValueError()
        raw = base64.b64decode(encoded, validate=True)
        if len(raw) > 2 * 1024 * 1024:
            raise ValueError()
        with Image.open(io.BytesIO(raw)) as image:
            if (
                image.format not in {"JPEG", "PNG", "WEBP"}
                or image.width * image.height > 20_000_000
            ):
                raise ValueError()
            image.load()
            normalized = ImageOps.exif_transpose(image).convert("RGB")
            normalized.thumbnail((1200, 1200))
            output = io.BytesIO()
            normalized.save(output, format="JPEG", quality=85)
            return output.getvalue()
    except (
        ValueError,
        binascii.Error,
        UnidentifiedImageError,
        OSError,
        Image.DecompressionBombError,
    ):
        raise DomainError(
            "Usa una imagen JPG, PNG o WEBP válida de hasta 2 MB.", 422
        ) from None


class AnimalService:
    def __init__(self, connection):
        self.repo = AnimalRepository(connection)

    def publish(self, user_id, data):
        images = [image_bytes(value) for value in [data.foto, *data.fotos]]
        pet_id = self.repo.create(user_id, data)
        for order, image in enumerate(images):
            self.repo.photo(pet_id, order, image)
        return next(p for p in self.repo.list() if p["id"] == pet_id)
