import pytest
from aioresponses import aioresponses

from aiohttp_oauth2_client.client import OAuth2Client
from aiohttp_oauth2_client.grant.client_credentials import ClientCredentialsGrant
from ..conftest import TOKEN_ENDPOINT, assert_request_with_access_token


CLIENT_ID = "test-client"
CLIENT_SECRET = "test-secret"


@pytest.mark.refresh_token(False)
class TestClientCredentialsGrant:
    async def test_fetch_token(self, mock_token: dict, mock_response: aioresponses):
        async with ClientCredentialsGrant(
            token_url=TOKEN_ENDPOINT,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        ) as grant:
            await grant.fetch_token()
            assert grant.token.access_token == mock_token["access_token"]
            assert mock_token.items() <= grant.token.items()

        # Access token request: https://datatracker.ietf.org/doc/html/rfc6749#autoid-51
        mock_response.assert_called_once_with(
            url=TOKEN_ENDPOINT,
            method="POST",
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
        )

    async def test_fetch_token_optional_parameters(
        self, mock_token: dict, mock_response: aioresponses
    ):
        async with ClientCredentialsGrant(
            token_url=TOKEN_ENDPOINT,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope="profile email",
        ) as grant:
            await grant.fetch_token()
            assert grant.token.access_token == mock_token["access_token"]
            assert mock_token.items() <= grant.token.items()

        # Access token request: https://datatracker.ietf.org/doc/html/rfc6749#autoid-51
        mock_response.assert_called_once_with(
            url=TOKEN_ENDPOINT,
            method="POST",
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope": "profile email",
            },
        )

    async def test_client(self, mock_token: dict, mock_response: aioresponses):
        async with ClientCredentialsGrant(
            token_url=TOKEN_ENDPOINT,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        ) as grant, OAuth2Client(grant) as client:
            await assert_request_with_access_token(client, mock_token, mock_response)
