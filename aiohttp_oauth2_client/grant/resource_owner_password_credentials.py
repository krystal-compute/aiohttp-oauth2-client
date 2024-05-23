from typing import Optional

from aiohttp_oauth2_client.grant.common import OAuth2Grant
from aiohttp_oauth2_client.models.request import (
    ResourceOwnerPasswordCredentialsAccessTokenRequest,
)
from aiohttp_oauth2_client.models.token import Token


class ResourceOwnerPasswordCredentialsGrant(OAuth2Grant):
    """
    OAuth 2.0 Resource Owner Password Credentials grant.

    Use the username and password of the resource owner to obatain an access token.
    """

    def __init__(
        self,
        token_url: str,
        username: str,
        password: str,
        token: Optional[dict] = None,
        **kwargs,
    ):
        """

        :param token_url: OAuth 2.0 Token URL
        :param username: username of the resource owner
        :param password: password of the resource owner
        :param token: OAuth 2.0 Token
        """
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
