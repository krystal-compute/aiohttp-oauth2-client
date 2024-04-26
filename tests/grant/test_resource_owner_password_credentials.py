from aiohttp_oauth2_client.client import OAuth2Client
from aiohttp_oauth2_client.grant.resource_owner_password_credentials import (
    ResourceOwnerPasswordCredentialsGrant,
)
from aioresponses import aioresponses
from ..conftest import TOKEN_ENDPOINT, assert_request_with_access_token

USERNAME = "test_username"
PASSWORD = "test_password"


async def test_fetch_token(mock_token: dict, mock_response: aioresponses):
    async with ResourceOwnerPasswordCredentialsGrant(
        token_url=TOKEN_ENDPOINT, username=USERNAME, password=PASSWORD
    ) as grant:
        await grant.fetch_token()
        assert grant.token.access_token == mock_token["access_token"]
        assert mock_token.items() <= grant.token.items()

    # Access token request: https://datatracker.ietf.org/doc/html/rfc6749#autoid-47
    mock_response.assert_called_once_with(
        url=TOKEN_ENDPOINT,
        method="POST",
        data={"grant_type": "password", "username": USERNAME, "password": PASSWORD},
    )


async def test_fetch_token_optional_parameters(
    mock_token: dict, mock_response: aioresponses
):
    async with ResourceOwnerPasswordCredentialsGrant(
        token_url=TOKEN_ENDPOINT,
        username=USERNAME,
        password=PASSWORD,
        client_id="test_client",
        scope="profile email",
    ) as grant:
        await grant.fetch_token()
        assert grant.token.access_token == mock_token["access_token"]
        assert mock_token.items() <= grant.token.items()

    # Access token request: https://datatracker.ietf.org/doc/html/rfc6749#autoid-47
    mock_response.assert_called_once_with(
        url=TOKEN_ENDPOINT,
        method="POST",
        data={
            "grant_type": "password",
            "username": USERNAME,
            "password": PASSWORD,
            "client_id": "test_client",
            "scope": "profile email",
        },
    )


async def test_client(mock_token: dict, mock_response: aioresponses):
    async with ResourceOwnerPasswordCredentialsGrant(
        token_url=TOKEN_ENDPOINT, username=USERNAME, password=PASSWORD
    ) as grant, OAuth2Client(grant) as client:
        await assert_request_with_access_token(client, mock_token, mock_response)
