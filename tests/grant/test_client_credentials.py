import pytest
from aioresponses import aioresponses

from aiohttp_oauth2_client.client import OAuth2Client
from aiohttp_oauth2_client.grant.client_credentials import ClientCredentialsGrant
from ..conftest import assert_request_with_access_token
from constants import TOKEN_ENDPOINT
from ..mock.response import add_token_request

CLIENT_ID = "test-client"
CLIENT_SECRET = "test-secret"


@pytest.mark.refresh_token(False)
class TestClientCredentialsGrant:
    async def test_fetch_token(self, mock_token: dict, mock_responses: aioresponses):
        add_token_request(mock_responses, mock_token)
        async with ClientCredentialsGrant(
            token_url=TOKEN_ENDPOINT,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        ) as grant:
            await grant.fetch_token()
            assert grant.token.access_token == mock_token["access_token"]
            assert mock_token.items() <= grant.token.model_dump().items()

        # Access token request: https://datatracker.ietf.org/doc/html/rfc6749#autoid-51
        mock_responses.assert_called_once_with(
            url=TOKEN_ENDPOINT,
            method="POST",
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
        )

    async def test_fetch_token_optional_parameters(
        self, mock_token: dict, mock_responses: aioresponses
    ):
        add_token_request(mock_responses, mock_token)
        async with ClientCredentialsGrant(
            token_url=TOKEN_ENDPOINT,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope="profile email",
        ) as grant:
            await grant.fetch_token()
            assert grant.token.access_token == mock_token["access_token"]
            assert mock_token.items() <= grant.token.model_dump().items()

        # Access token request: https://datatracker.ietf.org/doc/html/rfc6749#autoid-51
        mock_responses.assert_called_once_with(
            url=TOKEN_ENDPOINT,
            method="POST",
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope": "profile email",
            },
        )

    async def test_refresh_token(
        self, mock_token: dict, mock_token2: dict, mock_responses: aioresponses
    ):
        add_token_request(mock_responses, mock_token)
        add_token_request(mock_responses, mock_token2)
        async with ClientCredentialsGrant(
            token_url=TOKEN_ENDPOINT,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        ) as grant:
            await grant.fetch_token()
            await grant.refresh_token()

            assert grant.token.access_token == mock_token2["access_token"]
            assert mock_token2.items() <= grant.token.model_dump().items()

            # No refresh token for client credentials, just use client_credentials grant
            mock_responses.assert_called_with(
                url=TOKEN_ENDPOINT,
                method="POST",
                data={
                    "grant_type": "client_credentials",
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                },
            )

    async def test_client(self, mock_token: dict, mock_responses: aioresponses):
        add_token_request(mock_responses, mock_token)
        async with ClientCredentialsGrant(
            token_url=TOKEN_ENDPOINT,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        ) as grant, OAuth2Client(grant) as client:
            await assert_request_with_access_token(client, mock_token, mock_responses)

    async def test_client_refresh(
        self, mock_token: dict, mock_token2, mock_responses: aioresponses
    ):
        add_token_request(mock_responses, mock_token)
        add_token_request(mock_responses, mock_token2)
        async with ClientCredentialsGrant(
            token_url=TOKEN_ENDPOINT,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        ) as grant, OAuth2Client(grant) as client:
            await assert_request_with_access_token(client, mock_token, mock_responses)
            grant.token.expires_at = 1  # set token to be expired
            assert grant.token.is_expired()
            await assert_request_with_access_token(client, mock_token2, mock_responses)
