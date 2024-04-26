from typing import Optional, Union

from yarl import URL

from aiohttp_oauth2_client.grant.common import OAuth2Grant, GrantType


class ClientCredentialsGrant(OAuth2Grant):
    """
    OAuth2 Client Credentials grant.

    Use client credentials to obtain an access token.

    https://datatracker.ietf.org/doc/html/rfc6749#section-4.4
    """

    def __init__(
        self,
        token_url: Union[str, URL],
        client_id: str,
        client_secret: str,
        token: Optional[dict] = None,
        **kwargs,
    ):
        """

        :param token_url: OAuth 2.0 Token URL
        :param client_id: client identifier
        :param client_secret: client secret
        :param token: OAuth 2.0 Token
        :param kwargs: extra arguments used in token request
        """
        super().__init__(token_url, token, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    async def _fetch_token(self):
        data = dict(
            grant_type=GrantType.CLIENT_CREDENTIALS,
            client_id=self.client_id,
            client_secret=self.client_secret,
            **self.kwargs,
        )
        response = await self.execute_token_request(data)
        return await response.json()

    async def refresh_token(self):
        if "refresh_token" in self.token:
            # some clients may issue refresh tokens for the client credentials flow,
            # even though it is not officially in the specification
            await super().refresh_token()

        # just get a new token using the client credentials
        await self.fetch_token()
