import asyncio
from abc import abstractmethod
from typing import Optional, Union

import aiohttp
from aiohttp.typedefs import LooseHeaders
from yarl import URL

from aiohttp_oauth2_client.models.request import (
    AccessTokenRequest,
    RefreshTokenAccessTokenRequest,
)
from aiohttp_oauth2_client.models.token import Token


class OAuth2Grant:
    """
    Generic OAuth2 Grant class.
    """

    def __init__(
        self, token_url: Union[str, URL], token: Optional[dict] = None, **kwargs
    ):
        """
        :param token_url: OAuth 2.0 Token URL
        :param token: OAuth 2.0 Token
        :param kwargs: extra arguments used in token request
        """
        self.token_url = URL(token_url)
        self.token = Token.model_validate(token) if token else None
        self.token_refresh_lock = asyncio.Lock()
        self.session = aiohttp.ClientSession()
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self.close()

    async def close(self):
        """
        Close the Grant object and its associated resources.
        """
        await self.session.close()

    # @property
    # def token(self) -> OAuth2Token:
    #     return self.token_auth.token
    #
    # @token.setter
    # def token(self, token):
    #     self.token_auth.set_token(token)

    async def ensure_active_token(self):
        async with self.token_refresh_lock:
            if self.token.is_expired():
                await self.refresh_token()

    async def prepare_request(self, headers: Optional[LooseHeaders]):
        """
        Prepare the HTTP request by adding the OAuth 2.0 access token to the Authorization header.

        :param headers: HTTP request headers
        :return: updated HTTP request headers
        """
        headers = dict(headers) if headers else {}
        if not self.token:
            # request initial token
            await self.fetch_token()
        await self.ensure_active_token()
        headers["Authorization"] = f"Bearer {self.token.access_token}"
        return headers

    async def fetch_token(self):
        """
        Fetch an OAuth 2.0 token from the token endpoint and store it for subsequent use.
        """
        self.token = Token.model_validate(await self._fetch_token())

    @abstractmethod
    async def _fetch_token(self) -> dict:
        """
        Fetch an OAuth 2.0 token from the token endpoint.
        :return: OAuth 2.0 Token
        """
        ...

    async def refresh_token(self):
        """
        Obtain a new access token using the refresh token grant and store it for subsequent use.
        """
        access_token_request = RefreshTokenAccessTokenRequest(
            refresh_token=self.token.refresh_token,
            **self.kwargs,
        )
        response = await self.execute_token_request(access_token_request)
        self.token = Token.model_validate(await response.json())

    async def execute_token_request(self, data: AccessTokenRequest):
        return await self.session.post(
            url=self.token_url,
            data=data.model_dump(exclude_none=True),
        )
