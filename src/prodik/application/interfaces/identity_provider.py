from typing import Protocol

from prodik.application.interfaces.token_manager import UserData


class IdentityProvider(Protocol):
    def get_user_meta(self) -> UserData: ...
    def get_current_ip(self) -> str: ...
