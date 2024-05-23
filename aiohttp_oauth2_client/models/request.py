from typing import Optional

from pydantic import BaseModel, ConfigDict

from aiohttp_oauth2_client.models.grant import GrantType


class AccessTokenRequest(BaseModel):
    """
    Base model for OAuth 2.0 access token request.
    """

    grant_type: str
    """OAuth 2.0 grant type"""

    model_config = ConfigDict(extra="allow")


class AuthorizationCodeAccessTokenRequest(AccessTokenRequest):
    """
    Request model for the access token request with the Authorization Code grant.

    https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.3
    """

    grant_type: str = GrantType.AUTHORIZATION_CODE

    code: str
    """Authorization code received from the authorization server"""

    redirect_uri: Optional[str] = None
    """Redirect URI"""

    client_id: str
    """Client identifier"""


class ClientCredentialsAccessTokenRequest(AccessTokenRequest):
    """
    Request model for the access token request with the Client Credentials grant.

    https://datatracker.ietf.org/doc/html/rfc6749#section-4.4.2
    """

    grant_type: str = GrantType.CLIENT_CREDENTIALS

    client_id: str
    """Client identifier"""

    client_secret: str
    """Client secret"""

    scope: Optional[str] = None
    """Scope of the access request"""


class ResourceOwnerPasswordCredentialsAccessTokenRequest(AccessTokenRequest):
    """
    Request model for the access token request with the Resource Owner Password Credentials grant.

    https://datatracker.ietf.org/doc/html/rfc6749#section-4.3.2
    """

    grant_type: str = GrantType.RESOURCE_OWNER_PASSWORD_CREDENTIALS

    username: str
    """Resource owner username"""

    password: str
    """Resource owner password"""

    scope: Optional[str] = None
    """Scope of the access request"""


class RefreshTokenAccessTokenRequest(AccessTokenRequest):
    """
    Request model for the access token request using a Refresh Token.

    https://datatracker.ietf.org/doc/html/rfc6749#section-6
    """

    grant_type: str = GrantType.REFRESH_TOKEN

    refresh_token: str
    """Refresh token"""

    scope: Optional[str] = None
    """Scope of the access request"""


class DeviceAccessTokenRequest(AccessTokenRequest):
    """
    The Device Access Token Request model.

    https://datatracker.ietf.org/doc/html/rfc8628#section-3.4

    :ivar grant_type: The grant type. Value MUST be set to "urn:ietf:params:oauth:grant-type:device_code".
    :ivar device_code: The device verification code, "device_code" from the device authorization response.
    :ivar client_id: The client identifier.
    """

    grant_type: str = GrantType.DEVICE_CODE

    device_code: str
    """Device verification code"""

    client_id: str
    """Client identifier"""


class AuthorizationRequest(BaseModel):
    """
    The Authorization Request model.

    https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.1
    """

    response_type: str = "code"

    client_id: str
    """Client identifier"""

    redirect_uri: Optional[str] = None
    """Redirect URI"""

    scope: Optional[str] = None
    """Scope of the access request"""

    state: Optional[str] = None
    """Opaque value used by the client to maintain state between the request and callback"""


class AuthorizationRequestPKCE(AuthorizationRequest):
    code_challenge: str
    """Code challenge"""

    code_challenge_method: str
    """Code challenge method"""


class DeviceAuthorizationRequest(BaseModel):
    """
    The Device Authorization Request model.

    https://datatracker.ietf.org/doc/html/rfc8628#section-3.1
    """

    client_id: str
    """Client identifier"""

    scope: Optional[str] = None
    """Scope of the access request"""


class DeviceAuthorizationRequestPKCE(DeviceAuthorizationRequest):
    code_challenge: str
    """Code challenge"""

    code_challenge_method: str
    """Code challenge method"""
