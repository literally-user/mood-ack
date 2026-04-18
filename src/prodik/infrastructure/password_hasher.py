from dataclasses import dataclass

from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerifyMismatchError

from prodik.application.interfaces.password_hasher import PasswordHasher


@dataclass
class PasswordHasherImpl(PasswordHasher):
    _hasher = Argon2Hasher()

    def hash(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify(self, hashed_password: str, password: str) -> bool:
        try:
            return self._hasher.verify(hashed_password, password)
        except VerifyMismatchError:
            return False
