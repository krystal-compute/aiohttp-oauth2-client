import asyncio

from aioresponses import aioresponses

from aiohttp_oauth2_client.grant.authorization_code import AuthorizationCodeGrant
from ..constants import TOKEN_ENDPOINT, AUTHORIZATION_ENDPOINT
from ..mock.response import add_token_request
from ..mock.webbrowser import mock_browser_side_effect
import nest_asyncio

nest_asyncio.apply()

CLIENT_ID = "client_id"


async def test_fetch_token(mock_token: dict, mock_responses: aioresponses, mocker):
    # set up mock responses
    mock_browser = mocker.patch("webbrowser.open")
    loop = asyncio.get_event_loop()
    mock_browser.side_effect = lambda x: loop.run_until_complete(
        mock_browser_side_effect(x)
    )
    add_token_request(mock_responses, mock_token)

    async with AuthorizationCodeGrant(
        token_url=TOKEN_ENDPOINT,
        authorization_url=AUTHORIZATION_ENDPOINT,
        client_id=CLIENT_ID,
    ) as grant:
        await grant.fetch_token()
        assert grant.token.access_token == mock_token["access_token"]
        assert mock_token.items() <= grant.token.model_dump().items()
        mock_browser.assert_called()
