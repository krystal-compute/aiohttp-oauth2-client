from aiohttp_oauth2_client.grant.common import OAuth2Grant


class AuthorizationCodeGrant(OAuth2Grant):
    """
    OAuth2 Authorization Code grant.

    Use a browser login to request an authorization code, which is then used to request an access token.

    https://datatracker.ietf.org/doc/html/rfc6749#section-4.1
    """

    ...


# TODO: support PKCE
