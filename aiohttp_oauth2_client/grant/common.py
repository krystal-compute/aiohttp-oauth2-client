import asyncio
from abc import abstractmethod
from typing import Optional, Union

import aiohttp
from pydantic import ValidationError
from yarl import URL

from aiohttp_oauth2_client.models.errors import OAuth2Error
from aiohttp_oauth2_client.models.request import (
    AccessTokenRequest,
    RefreshTokenAccessTokenRequest,
)
from aiohttp_oauth2_client.models.response import ErrorResponse
from aiohttp_oauth2_client.models.token import Token


class OAuth2Grant:
    """
    Generic OAuth 2.0 Grant class.
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
        self.lock = asyncio.Lock()
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

    async def ensure_active_token(self):
        """
        Ensure that the stored access token is still active.
        If this is not the case, the token will be refreshed.
        """
        async with self.lock:
            if self.token.is_expired():
                await self.refresh_token()

    async def prepare_headers(self):
        """
        Prepare the HTTP request headers by adding the OAuth 2.0 access token to the Authorization header.

        :return: HTTP request headers with Authorization header
        """
        headers = {}
        async with self.lock:
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
        self.token = await self._fetch_token()

    @abstractmethod
    async def _fetch_token(self) -> Token:
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
        self.token = await self.execute_token_request(access_token_request)

    async def execute_token_request(self, data: AccessTokenRequest) -> Token:
        """
        Execute a token request with the provided data.

        :param data: token request data
        :return: OAuth 2.0 Token
        :raises OAuth2Error: if the token request fails
        :raises aiohttp.ClientResponseError: if the HTTP error cannot be parsed as an OAuth 2.0 error response
        """
        async with self.session.post(
            url=self.token_url,
            data=data.model_dump(exclude_none=True),
        ) as response:
            if not response.ok:
                try:
                    raise OAuth2Error(
                        ErrorResponse.model_validate(await response.json())
                    )
                except ValidationError:
                    response.raise_for_status()
            return Token.model_validate(await response.json())
