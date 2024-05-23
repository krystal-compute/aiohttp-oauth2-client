import asyncio
import contextlib
import time
from typing import Optional, Union

import aiohttp.web
from yarl import URL

from aiohttp_oauth2_client.grant.common import OAuth2Grant
from aiohttp_oauth2_client.models.errors import AuthError
from aiohttp_oauth2_client.models.request import (
    AuthorizationRequest,
    AuthorizationCodeAccessTokenRequest,
    AuthorizationRequestPKCE,
)
from aiohttp_oauth2_client.models.response import AuthorizationResponse
from aiohttp_oauth2_client.models.token import Token
from aiohttp_oauth2_client.models.pkce import PKCE
import webbrowser


class AuthorizationCodeGrant(OAuth2Grant):
    """
    OAuth 2.0 Authorization Code grant.

    Use a browser login to request an authorization code, which is then used to request an access token.

    https://datatracker.ietf.org/doc/html/rfc6749#section-4.1
    """

    timeout: int = 300

    def __init__(
        self,
        token_url: Union[str, URL],
        authorization_url: Union[str, URL],
        client_id: str,
        token: Optional[dict] = None,
        pkce: bool = False,
        _web_server_port: Optional[int] = None,
        **kwargs,
    ):
        """

        :param token_url: OAuth 2.0 Token URL
        :param authorization_url: OAuth 2.0 Authorization URL
        :param client_id: client identifier
        :param token: OAuth 2.0 Token
        :param pkce: use PKCE
        :param _web_server_port: web server port for handling redirect callback, leave empty for random available port
        """
        super().__init__(token_url, token, **kwargs)
        self.authorization_url = URL(authorization_url)
        self.client_id = client_id
        self.pkce = PKCE() if pkce else None
        self._web_server_port = _web_server_port

    async def _fetch_token(self) -> Token:
        time_start = time.time()
        async with _web_server(port=self._web_server_port or 0) as (socket_info, state):
            redirect_uri = URL.build(
                scheme="http", host="localhost", port=socket_info[1], path="/callback"
            )
            if self.pkce:
                authorization_request = AuthorizationRequestPKCE(
                    client_id=self.client_id,
                    redirect_uri=str(redirect_uri),
                    code_challenge=self.pkce.code_challenge,
                    code_challenge_method=self.pkce.code_challenge_method,
                    **self.kwargs,
                )
            else:
                authorization_request = AuthorizationRequest(
                    client_id=self.client_id,
                    redirect_uri=str(redirect_uri),
                    **self.kwargs,
                )
            full_authz_url = self.authorization_url % authorization_request.model_dump(
                exclude_none=True
            )
            webbrowser.open(str(full_authz_url))
            while not state and not time.time() > time_start + self.timeout:
                await asyncio.sleep(1)
            if not state:
                raise AuthError("Authorization timed out.")
            authorization = AuthorizationResponse.model_validate(state)

        token_request = AuthorizationCodeAccessTokenRequest(
            code=authorization.code,
            redirect_uri=authorization_request.redirect_uri,
            client_id=self.client_id,
        )
        if self.pkce:
            token_request.code_verifier = str(self.pkce.code_verifier, encoding="utf-8")
        return await self.execute_token_request(token_request)


@contextlib.asynccontextmanager
async def _web_server(port: int):
    """
    Launch a web server to handle the redirect after the authorization request.
    Stores the authorization code in the state.
    """
    state = dict()

    async def _request_handler(request: aiohttp.web.Request) -> aiohttp.web.Response:
        if request.path == "/callback":
            state.update(request.query)
            return aiohttp.web.Response(
                text="Authorization successful! You can close this window now.",
                status=200,
            )
        else:
            return aiohttp.web.Response(status=404)

    server = aiohttp.web.Server(_request_handler)
    runner = aiohttp.web.ServerRunner(server)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, port=port)
    await site.start()
    socket_info = site._server.sockets[0].getsockname()
    yield socket_info, state
    await site.stop()
