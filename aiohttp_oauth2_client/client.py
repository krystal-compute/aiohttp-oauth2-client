from typing import Optional

import aiohttp
from aiohttp import ClientResponse as ClientResponse
from aiohttp.typedefs import StrOrURL, LooseHeaders

from aiohttp_oauth2_client.grant.common import OAuth2Grant


class OAuth2Client(aiohttp.ClientSession):
    """
    The `OAuth2Client` is an :py:class:`aiohttp.ClientSession` with support for OAuth2 access tokens.
    """

    def __init__(self, grant: OAuth2Grant, **kwargs):
        """
        :param grant: OAuth2Grant object providing an OAuth2 grant implementation.
        """
        super().__init__(**kwargs)
        self.grant = grant

    async def _request(
        self,
        method: str,
        str_or_url: StrOrURL,
        *,
        headers: Optional[LooseHeaders] = None,
        **kwargs,
    ) -> ClientResponse:
        headers = await self.grant.prepare_request(headers)
        return await super()._request(method, str_or_url, headers=headers, **kwargs)
