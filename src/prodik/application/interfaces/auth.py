from dataclasses import dataclass
from typing import Protocol


@dataclass
class OAuthClientResponse:
    access_token: str
    refresh_token: str
    expires_in: int
    token_id: str


class OAuthClient(Protocol):
    async def exchange_code(self, authorization_code: str) -> OAuthClientResponse: ...
