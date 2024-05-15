from aioresponses import aioresponses

from aiohttp_oauth2_client.grant.device_code import DeviceCodeGrant
from aiohttp_oauth2_client.models.response import DeviceAuthorizationResponse
from conftest import TOKEN_ENDPOINT, DEVICE_AUTHORIZATION_ENDPOINT

CLIENT_ID = "test-client"


async def test_fetch_token(mock_token: dict, mock_response: aioresponses):
    async with DeviceCodeGrant(
        token_url=TOKEN_ENDPOINT,
        device_authorization_url=DEVICE_AUTHORIZATION_ENDPOINT,
        client_id=CLIENT_ID,
    ) as grant:
        mock_authorization_response = DeviceAuthorizationResponse(
            device_code="device-code",
            user_code="user-code",
            verification_uri="verification-uri",
            expires_in=300,
            interval=5,
        )
        mock_response.post(
            DEVICE_AUTHORIZATION_ENDPOINT,
            status=200,
            payload=mock_authorization_response.model_dump(),
        )

        await grant.fetch_token()
        assert grant.token.access_token == mock_token["access_token"]
        assert mock_token.items() <= grant.token.model_dump().items()

        mock_response.assert_called_with(
            url=DEVICE_AUTHORIZATION_ENDPOINT,
            method="POST",
            data={"client_id": CLIENT_ID},
        )

        mock_response.assert_called_with(
            url=TOKEN_ENDPOINT,
            method="POST",
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": mock_authorization_response.device_code,
                "client_id": CLIENT_ID,
            },
        )
