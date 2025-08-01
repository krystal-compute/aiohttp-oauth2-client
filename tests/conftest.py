import asyncio

import nest_asyncio
import pytest
from aiohttp import ClientRequest
from aioresponses import aioresponses
from multidict import CIMultiDict

from aiohttp_oauth2_client.middleware import OAuth2Middleware
from .constants import TOKENS
from .mock.webbrowser import mock_browser_side_effect

nest_asyncio.apply()


@pytest.fixture
def mock_token(request) -> dict:
    marker_refresh_token = request.node.get_closest_marker("refresh_token")
    refresh_token = marker_refresh_token.args[0] if marker_refresh_token else True
    token = TOKENS[0].copy()
    if not refresh_token:
        token.pop("refresh_token")
        token.pop("refresh_expires_in")
    return token


@pytest.fixture
def mock_token2(request) -> dict:
    marker_refresh_token = request.node.get_closest_marker("refresh_token")
    refresh_token = marker_refresh_token.args[0] if marker_refresh_token else True
    token = TOKENS[1].copy()
    if not refresh_token:
        token.pop("refresh_token")
        token.pop("refresh_expires_in")
    return token


@pytest.fixture
async def mock_responses() -> aioresponses:
    with aioresponses(
        passthrough=["http://localhost", "http://0.0.0.0", "http://127.0.0.1"]
    ) as mock:
        yield mock


@pytest.fixture
async def mock_browser(mocker):
    browser = mocker.patch("webbrowser.open")
    loop = asyncio.get_event_loop()
    browser.side_effect = lambda x: loop.run_until_complete(mock_browser_side_effect(x))
    return browser


@pytest.fixture
async def mock_request(mocker) -> ClientRequest:
    request = mocker.MagicMock(spec=ClientRequest)
    request.headers = CIMultiDict()
    return request


async def assert_request_with_access_token(
    oauth2_middleware: OAuth2Middleware, request: ClientRequest, token: dict
):
    await oauth2_middleware.authenticate(request)
    assert request.headers["Authorization"] == f"Bearer {token['access_token']}"
