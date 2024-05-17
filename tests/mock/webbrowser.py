import aiohttp
from yarl import URL

from aiohttp_oauth2_client.models.response import AuthorizationResponse


async def mock_browser_side_effect(*args, **kwargs):
    url = URL(args[0])
    # catch callback URL and add authorization response to query parameters
    callback = URL(url.query.get("redirect_uri")) % AuthorizationResponse(
        code="authorization-code"
    ).model_dump(exclude_none=True)
    # mock the redirect call
    async with aiohttp.ClientSession() as session:
        async with session.get(callback) as resp:
            assert resp.status == 200
