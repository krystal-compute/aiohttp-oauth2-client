from aioresponses import aioresponses

from constants import TOKEN_ENDPOINT


def add_token_request(mock: aioresponses, token: dict):
    mock.post(TOKEN_ENDPOINT, status=200, payload=token)
