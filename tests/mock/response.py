from aioresponses import aioresponses

from aiohttp_oauth2_client.models.response import (
    ErrorResponse,
    DeviceAuthorizationResponse,
)

from ..constants import TOKEN_ENDPOINT, DEVICE_AUTHORIZATION_ENDPOINT


def add_token_request(mock: aioresponses, token: dict):
    mock.post(TOKEN_ENDPOINT, status=200, payload=token)


def add_token_request_error(mock: aioresponses, error: ErrorResponse):
    mock.post(TOKEN_ENDPOINT, status=400, payload=error.model_dump(exclude_none=True))


def add_device_authorization_request(
    mock: aioresponses, response: DeviceAuthorizationResponse
):
    mock.post(
        DEVICE_AUTHORIZATION_ENDPOINT,
        status=200,
        payload=response.model_dump(exclude_none=True),
    )
