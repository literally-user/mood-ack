from dataclasses import dataclass

from httpx import AsyncClient

from prodik.application.interfaces.auth import OAuthClient, OAuthClientResponse
from prodik.infrastructure.config import KeyCloakConfig

@dataclass
class KeycloakOAuthClient(OAuthClient):
    config: KeyCloakConfig
    transport: AsyncClient

    async def exchange_code(self, authorization_code: str) -> OAuthClientResponse:
        response = await self.transport.post(
            "https://credentials.literally.io/token",
            data={
                "grant_type": "authorization_code",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "code": authorization_code,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

        content = response.json()

        return OAuthClientResponse(
            access_token=content['access_token'],
            refresh_token=content['refresh_token'],
            expires_in=content['expires_in'],
            token_id=content['token_id'],
        )