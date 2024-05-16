from aioresponses import aioresponses
from yarl import URL

from aiohttp_oauth2_client.client import OAuth2Client
from aiohttp_oauth2_client.grant.device_code import DeviceCodeGrant
from aiohttp_oauth2_client.models.response import (
    DeviceAuthorizationResponse,
    ErrorResponse,
)
from ..conftest import assert_request_with_access_token
from ..constants import TOKEN_ENDPOINT, DEVICE_AUTHORIZATION_ENDPOINT
from ..mock.response import (
    add_token_request,
    add_token_request_error,
    add_device_authorization_request,
)

CLIENT_ID = "test-client"
DEVICE_CODE = "device-code"

device_authorization_response = DeviceAuthorizationResponse(
    device_code=DEVICE_CODE,
    user_code="user-code",
    verification_uri="verification-uri",
    expires_in=300,
    interval=5,
)


async def test_fetch_token(mock_token: dict, mock_responses: aioresponses):
    # set up mock responses
    add_device_authorization_request(mock_responses, device_authorization_response)
    add_token_request(mock_responses, mock_token)

    async with DeviceCodeGrant(
        token_url=TOKEN_ENDPOINT,
        device_authorization_url=DEVICE_AUTHORIZATION_ENDPOINT,
        client_id=CLIENT_ID,
    ) as grant:
        await grant.fetch_token()
        assert grant.token.access_token == mock_token["access_token"]
        assert mock_token.items() <= grant.token.model_dump().items()

        # Device authorization request: https://datatracker.ietf.org/doc/html/rfc8628#section-3.1
        mock_responses.assert_called_with(
            url=DEVICE_AUTHORIZATION_ENDPOINT,
            method="POST",
            data={"client_id": CLIENT_ID},
        )
        # Device access token request: https://datatracker.ietf.org/doc/html/rfc8628#section-3.4
        mock_responses.assert_called_with(
            url=TOKEN_ENDPOINT,
            method="POST",
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": DEVICE_CODE,
                "client_id": CLIENT_ID,
            },
        )


async def test_wait_for_token(mock_token: dict, mock_responses: aioresponses):
    add_device_authorization_request(mock_responses, device_authorization_response)
    # first token request results in "authorization_pending" error
    add_token_request_error(
        mock_responses, error=ErrorResponse(error="authorization_pending")
    )
    # second token requests is successful
    add_token_request(mock_responses, mock_token)

    async with DeviceCodeGrant(
        token_url=TOKEN_ENDPOINT,
        device_authorization_url=DEVICE_AUTHORIZATION_ENDPOINT,
        client_id=CLIENT_ID,
    ) as grant:
        await grant.fetch_token()
        assert grant.token.access_token == mock_token["access_token"]
        assert mock_token.items() <= grant.token.model_dump().items()

        mock_responses.assert_called()
        assert len(mock_responses.requests[("POST", URL(TOKEN_ENDPOINT))]) == 2


async def test_refresh_token(
    mock_token: dict, mock_token2: dict, mock_responses: aioresponses
):
    add_device_authorization_request(mock_responses, device_authorization_response)
    add_token_request(mock_responses, mock_token)
    add_token_request(mock_responses, mock_token2)

    async with DeviceCodeGrant(
        token_url=TOKEN_ENDPOINT,
        device_authorization_url=DEVICE_AUTHORIZATION_ENDPOINT,
        client_id=CLIENT_ID,
    ) as grant:
        await grant.fetch_token()
        await grant.refresh_token()

        assert grant.token.access_token == mock_token2["access_token"]
        assert mock_token2.items() <= grant.token.model_dump().items()

        # Refresh token grant: https://datatracker.ietf.org/doc/html/rfc6749#section-6
        mock_responses.assert_called_with(
            url=TOKEN_ENDPOINT,
            method="POST",
            data={
                "grant_type": "refresh_token",
                "refresh_token": mock_token["refresh_token"],
            },
        )


async def test_pkce(mock_token: dict, mock_responses: aioresponses):
    add_device_authorization_request(mock_responses, device_authorization_response)
    add_token_request(mock_responses, mock_token)
    async with DeviceCodeGrant(
        token_url=TOKEN_ENDPOINT,
        device_authorization_url=DEVICE_AUTHORIZATION_ENDPOINT,
        client_id=CLIENT_ID,
        pkce=True,
    ) as grant:
        await grant.fetch_token()
        assert grant.token.access_token == mock_token["access_token"]
        assert mock_token.items() <= grant.token.model_dump().items()

        # Device authorization request: https://datatracker.ietf.org/doc/html/rfc8628#section-3.1
        mock_responses.assert_called_with(
            url=DEVICE_AUTHORIZATION_ENDPOINT,
            method="POST",
            data={
                "client_id": CLIENT_ID,
                "code_challenge": grant.pkce.code_challenge.decode("utf-8"),
                "code_challenge_method": "S256",
            },
        )
        # Device access token request: https://datatracker.ietf.org/doc/html/rfc8628#section-3.4
        mock_responses.assert_called_with(
            url=TOKEN_ENDPOINT,
            method="POST",
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": DEVICE_CODE,
                "client_id": CLIENT_ID,
                "code_verifier": grant.pkce.code_verifier.decode("utf-8"),
            },
        )


async def test_client(mock_token: dict, mock_responses: aioresponses):
    add_device_authorization_request(mock_responses, device_authorization_response)
    add_token_request(mock_responses, mock_token)
    async with DeviceCodeGrant(
        token_url=TOKEN_ENDPOINT,
        device_authorization_url=DEVICE_AUTHORIZATION_ENDPOINT,
        client_id=CLIENT_ID,
    ) as grant, OAuth2Client(grant) as client:
        await assert_request_with_access_token(client, mock_token, mock_responses)


async def test_client_refresh(
    mock_token: dict, mock_token2: dict, mock_responses: aioresponses
):
    add_device_authorization_request(mock_responses, device_authorization_response)
    add_token_request(mock_responses, mock_token)
    add_token_request(mock_responses, mock_token2)
    async with DeviceCodeGrant(
        token_url=TOKEN_ENDPOINT,
        device_authorization_url=DEVICE_AUTHORIZATION_ENDPOINT,
        client_id=CLIENT_ID,
    ) as grant, OAuth2Client(grant) as client:
        await assert_request_with_access_token(client, mock_token, mock_responses)
        grant.token.expires_at = 1
        assert grant.token.is_expired()
        await assert_request_with_access_token(client, mock_token2, mock_responses)
