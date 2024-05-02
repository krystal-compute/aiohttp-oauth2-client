from typing import Optional

from aiohttp_oauth2_client.grant.common import OAuth2Grant
from aiohttp_oauth2_client.models.request import (
    ResourceOwnerPasswordCredentialsAccessTokenRequest,
)
from aiohttp_oauth2_client.models.token import Token


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

    async def _fetch_token(self) -> Token:
        access_token_request = ResourceOwnerPasswordCredentialsAccessTokenRequest(
            username=self.username,
            password=self.password,
            **self.kwargs,
        )
        token = await self.execute_token_request(access_token_request)
        return token
