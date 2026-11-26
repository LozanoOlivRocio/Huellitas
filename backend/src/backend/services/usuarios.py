import hashlib
import secrets
from pwdlib import PasswordHash
from backend.repositories.usuarios import UsuarioRepository, user_out
from backend.services.errors import DomainError

passwords = PasswordHash.recommended()
_dummy_hash = passwords.hash(secrets.token_urlsafe(24))


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class UsuarioService:
    def __init__(self, connection):
        self.repo = UsuarioRepository(connection)

    def register(self, data):
        if self.repo.by_email(str(data.email)):
            raise DomainError("Ya existe una cuenta con ese correo.", 409)
        return self.repo.create(data, passwords.hash(data.password.get_secret_value()))

    def login(self, data):
        user = self.repo.by_email(str(data.email))
        valid = passwords.verify(
            data.password.get_secret_value(),
            user["password_hash"] if user else _dummy_hash,
        )
        if not user or not valid or not user["activo"]:
            raise DomainError("El correo o la contraseña no son correctos.", 401)
        return user

    def session_user(self, token):
        return self.repo.session(token_digest(token)) if token else None

    def start_session(self, user, days):
        token = secrets.token_urlsafe(48)
        self.repo.create_session(user["id"], token_digest(token), days)
        return token, user_out(user)

    def logout(self, token):
        if token:
            self.repo.delete_session(token_digest(token))
