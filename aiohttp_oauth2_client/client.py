from typing import Optional

import aiohttp
from aiohttp import ClientResponse as ClientResponse
from aiohttp.typedefs import StrOrURL, LooseHeaders

from aiohttp_oauth2_client.grant.common import OAuth2Grant


class OAuth2Client(aiohttp.ClientSession):
    def __init__(self, oauth2_grant: OAuth2Grant, **kwargs):
        super().__init__(**kwargs)
        self.oauth2_grant = oauth2_grant

    async def _request(
        self,
        method: str,
        str_or_url: StrOrURL,
        *,
        headers: Optional[LooseHeaders] = None,
        **kwargs,
    ) -> ClientResponse:
        headers = await self.oauth2_grant.prepare_request(headers)
        return await super()._request(method, str_or_url, headers=headers, **kwargs)
