from aiohttp import ClientRequest, ClientResponse
from aiohttp.client_middlewares import ClientMiddlewareType, ClientHandlerType

from aiohttp_oauth2_client.grant.common import OAuth2Grant


class OAuth2Middleware(ClientMiddlewareType):
    """
    Client middleware to add OAuth2 access tokens in the authorization header of HTTP requests.
    """

    def __init__(self, grant: OAuth2Grant):
        self.grant = grant

    async def __call__(
        self, request: ClientRequest, handler: ClientHandlerType
    ) -> ClientResponse:
        await self.authenticate(request)
        response = await handler(request)
        return response

    async def authenticate(self, request: ClientRequest):
        """
        Add the OAuth2 access token to the request's Authorization header.
        :param request: ClientRequest object
        :return:
        """
        request.headers.update(await self.grant.prepare_headers())
