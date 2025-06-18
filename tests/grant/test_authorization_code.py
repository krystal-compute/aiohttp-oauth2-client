from aioresponses import aioresponses
from yarl import URL

from aiohttp_oauth2_client.grant.authorization_code import AuthorizationCodeGrant
from aiohttp_oauth2_client.middleware import OAuth2Middleware
from ..conftest import assert_request_with_access_token
from ..constants import TOKEN_ENDPOINT, AUTHORIZATION_ENDPOINT
from ..mock.response import add_token_request

CLIENT_ID = "client_id"


async def test_fetch_token(
    mock_token: dict, mock_responses: aioresponses, mock_browser
):
    # set up mock responses
    add_token_request(mock_responses, mock_token)

    async with AuthorizationCodeGrant(
        token_url=TOKEN_ENDPOINT,
        authorization_url=AUTHORIZATION_ENDPOINT,
        client_id=CLIENT_ID,
        _web_server_port=8080,
    ) as grant:
        await grant.fetch_token()
        assert grant.token.access_token == mock_token["access_token"]
        assert mock_token.items() <= grant.token.model_dump().items()
        mock_browser.assert_called_once()

        mock_browser_url = URL(mock_browser.call_args.args[0])
        authz_url = URL(AUTHORIZATION_ENDPOINT)
        assert mock_browser_url.host == authz_url.host
        assert mock_browser_url.path == authz_url.path
        assert mock_browser_url.query.get("client_id") == CLIENT_ID

        redirect_uri = mock_browser_url.query.get("redirect_uri")

        mock_responses.assert_called_once_with(
            url=TOKEN_ENDPOINT,
            method="POST",
            data={
                "grant_type": "authorization_code",
                "code": "authorization-code",
                "client_id": CLIENT_ID,
                "redirect_uri": redirect_uri,
            },
        )


async def test_refresh_token(
    mock_token: dict, mock_token2: dict, mock_responses: aioresponses, mock_browser
):
    add_token_request(mock_responses, mock_token)
    add_token_request(mock_responses, mock_token2)

    async with AuthorizationCodeGrant(
        token_url=TOKEN_ENDPOINT,
        authorization_url=AUTHORIZATION_ENDPOINT,
        client_id=CLIENT_ID,
        _web_server_port=8080,
    ) as grant:
        await grant.fetch_token()
        await grant.refresh_token()

        assert grant.token.access_token == mock_token2["access_token"]
        assert mock_token2.items() <= grant.token.model_dump().items()

        mock_responses.assert_called_with(
            url=TOKEN_ENDPOINT,
            method="POST",
            data={
                "grant_type": "refresh_token",
                "refresh_token": mock_token["refresh_token"],
            },
        )


async def test_pkce(mock_token: dict, mock_responses: aioresponses, mock_browser):
    add_token_request(mock_responses, mock_token)
    async with AuthorizationCodeGrant(
        token_url=TOKEN_ENDPOINT,
        authorization_url=AUTHORIZATION_ENDPOINT,
        client_id=CLIENT_ID,
        pkce=True,
        _web_server_port=8080,
    ) as grant:
        await grant.fetch_token()
        assert grant.token.access_token == mock_token["access_token"]

        mock_browser_url = URL(mock_browser.call_args.args[0])
        redirect_uri = mock_browser_url.query.get("redirect_uri")

        assert mock_browser_url.query.get(
            "code_challenge"
        ) == grant.pkce.code_challenge.decode("utf-8")
        assert mock_browser_url.query.get("code_challenge_method") == "S256"

        mock_responses.assert_called_with(
            url=TOKEN_ENDPOINT,
            method="POST",
            data={
                "grant_type": "authorization_code",
                "code": "authorization-code",
                "client_id": CLIENT_ID,
                "code_verifier": grant.pkce.code_verifier.decode("utf-8"),
                "redirect_uri": redirect_uri,
            },
        )


async def test_client(
    mock_request, mock_token: dict, mock_responses: aioresponses, mock_browser
):
    add_token_request(mock_responses, mock_token)
    async with AuthorizationCodeGrant(
        token_url=TOKEN_ENDPOINT,
        authorization_url=AUTHORIZATION_ENDPOINT,
        client_id=CLIENT_ID,
        _web_server_port=8080,
    ) as grant:
        mw = OAuth2Middleware(grant)
        await assert_request_with_access_token(mw, mock_request, mock_token)


async def test_client_refresh(
    mock_request,
    mock_token: dict,
    mock_token2: dict,
    mock_responses: aioresponses,
    mock_browser,
):
    add_token_request(mock_responses, mock_token)
    add_token_request(mock_responses, mock_token2)
    async with AuthorizationCodeGrant(
        token_url=TOKEN_ENDPOINT,
        authorization_url=AUTHORIZATION_ENDPOINT,
        client_id=CLIENT_ID,
        _web_server_port=8080,
    ) as grant:
        oauth2_middleware = OAuth2Middleware(grant)
        await assert_request_with_access_token(
            oauth2_middleware, mock_request, mock_token
        )
        grant.token.expires_at = 1
        assert grant.token.is_expired()
        await assert_request_with_access_token(
            oauth2_middleware, mock_request, mock_token2
        )
