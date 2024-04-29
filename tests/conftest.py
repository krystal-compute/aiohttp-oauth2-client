import pytest
from aioresponses import aioresponses

from aiohttp_oauth2_client.client import OAuth2Client

TEST_URL = "https://example.com/protected"
TOKEN_ENDPOINT = "https://sso.example.com/oauth2/token"
TOKENS = [
    {
        "access_token": "2YotnFZFEjr1zCsicMWpAA",
        "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
        "expires_in": 300,
        "refresh_expires_in": 1800,
        "token_type": "Bearer",
        "scope": "profile email",
    },
    {
        "access_token": "AYjcyMzY3ZDhiNmJkNTY",
        "refresh_token": "RjY2NjM5NzA2OWJjuE7c",
        "expires_in": 300,
        "refresh_expires_in": 1800,
        "token_type": "Bearer",
        "scope": "profile email",
    },
]


@pytest.fixture
def mock_token(request) -> dict:
    refresh_token = request.node.get_closest_marker("refresh_token", True).args[0]
    token = TOKENS[0].copy()
    if not refresh_token:
        token.pop("refresh_token")
        token.pop("refresh_expires_in")
    return token


@pytest.fixture
def mock_token2(request) -> dict:
    refresh_token = request.node.get_closest_marker("refresh_token", True).args[0]
    token = TOKENS[1].copy()
    if not refresh_token:
        token.pop("refresh_token")
        token.pop("refresh_expires_in")
    return token


@pytest.fixture
async def mock_response(mock_token) -> aioresponses:
    with aioresponses() as mock:
        mock.post(TOKEN_ENDPOINT, status=200, payload=mock_token)
        yield mock


@pytest.fixture
async def mock_response_refresh(mock_token, mock_token2) -> aioresponses:
    with aioresponses() as mock:
        mock.post(TOKEN_ENDPOINT, status=200, payload=mock_token)
        mock.post(TOKEN_ENDPOINT, status=200, payload=mock_token2)
        yield mock


async def assert_request_with_access_token(
    client: OAuth2Client, token: dict, responses: aioresponses
):
    # add mock response
    responses.get(TEST_URL, status=200, body="Hello!")
    response = await client.get(TEST_URL)
    assert response.status == 200

    responses.assert_called_with(
        url=TEST_URL,
        method="GET",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )


async def assert_token_refresh(
    client: OAuth2Client, token: dict, token2: dict, responses: aioresponses
):
    # add mock response
    responses.get(TEST_URL, status=200, body="Hello!")
    response = await client.get(TEST_URL)
    assert response.status == 200

    responses.assert_called_with(
        url=TEST_URL,
        method="GET",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
