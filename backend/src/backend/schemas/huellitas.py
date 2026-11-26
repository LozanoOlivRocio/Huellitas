from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator


class Input(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class UserOut(BaseModel):
    id: str
    nombre: str
    apellidos: str
    email: str
    telefono: str
    documento: str
    ubicacion: str


class Register(Input):
    nombre: str = Field(min_length=2, max_length=100)
    apellidos: str = Field(min_length=2, max_length=100)
    email: EmailStr
    telefono: str = Field(pattern=r"^[+0-9 ()-]{7,20}$")
    documento: str = Field(pattern=r"^[0-9]{8}$")
    ubicacion: str = Field(min_length=2, max_length=200)
    password: SecretStr = Field(min_length=8, max_length=128)


class Login(Input):
    email: EmailStr
    password: SecretStr = Field(min_length=1, max_length=128)


class PetInput(Input):
    nombre: str = Field(min_length=2, max_length=100)
    especie: Literal["Perro", "Gato", "Otro"]
    sexo: Literal["Macho", "Hembra", "Desconocido"]
    edad: str = Field(min_length=1, max_length=40)
    tamano: Literal["Pequeño", "Mediano", "Grande"]
    temperamento: str = Field(min_length=2, max_length=200)
    historia: str = Field(min_length=50, max_length=4000)
    ubicacion: str = Field(min_length=2, max_length=200)
    foto: str = Field(max_length=3_000_000)
    fotos: list[str] = Field(default_factory=list, max_length=4)
    vacunado: bool = False
    desparasitado: bool = False
    esterilizado: bool = False

    @field_validator("fotos")
    @classmethod
    def photo_lengths(cls, values):
        if any(len(v) > 3_000_000 for v in values):
            raise ValueError("Cada imagen debe pesar hasta 2 MB.")
        return values


class PetOut(BaseModel):
    id: int
    owner: str
    publicador: str
    nombre: str
    especie: str
    sexo: str
    edad: str
    tamano: str
    temperamento: str
    historia: str
    ubicacion: str
    foto: str
    fotos: list[str]
    vacunado: bool
    desparasitado: bool
    esterilizado: bool
    estado: Literal["disponible", "adoptado", "retirado"]


class ApplicationInput(Input):
    petId: int = Field(gt=0)
    vivienda: Literal[
        "Casa con jardín",
        "Departamento con protección",
        "Casa o departamento sin patio",
    ]
    otrasMascotas: bool
    ninos: bool
    motivacion: str = Field(min_length=30, max_length=2000)


class ResolveInput(Input):
    estado: Literal["aceptada", "rechazada", "cancelada"]


class MessageInput(Input):
    contenido: str = Field(min_length=1, max_length=2000)


class MessageOut(BaseModel):
    id: str
    sender: str
    contenido: str
    fecha: datetime


class ApplicationOut(BaseModel):
    id: str
    petId: int
    userId: str
    nombre: str
    vivienda: str
    otrasMascotas: bool
    ninos: bool
    motivacion: str
    estado: Literal["pendiente", "aceptada", "rechazada", "cancelada"]
    fecha: datetime
    mensajes: list[MessageOut]
