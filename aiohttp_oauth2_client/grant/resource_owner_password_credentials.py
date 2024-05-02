from typing import Optional

from aiohttp_oauth2_client.grant.common import OAuth2Grant
from aiohttp_oauth2_client.models.request import (
    ResourceOwnerPasswordCredentialsAccessTokenRequest,
)


class ResourceOwnerPasswordCredentialsGrant(OAuth2Grant):
    def __init__(
        self,
        token_url: str,
        username: str,
        password: str,
        token: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(token_url, token, **kwargs)
        self.username = username
        self.password = password

    async def _fetch_token(self) -> dict:
        access_token_request = ResourceOwnerPasswordCredentialsAccessTokenRequest(
            username=self.username,
            password=self.password,
            **self.kwargs,
        )
        response = await self.execute_token_request(access_token_request)
        response.raise_for_status()
        return await response.json()
