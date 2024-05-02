from typing import Optional

from pydantic import BaseModel, ConfigDict

from aiohttp_oauth2_client.models.grant import GrantType


class AccessTokenRequest(BaseModel):
    grant_type: str

    model_config = ConfigDict(extra="allow")


class ClientCredentialsAccessTokenRequest(AccessTokenRequest):
    """
    Request model for the access token request with the Client Credentials grant.

    https://datatracker.ietf.org/doc/html/rfc6749#section-4.4.2
    """

    grant_type: str = GrantType.CLIENT_CREDENTIALS
    client_id: str
    client_secret: str
    scope: Optional[str] = None


class ResourceOwnerPasswordCredentialsAccessTokenRequest(AccessTokenRequest):
    """
    Request model for the access token request with the Resource Owner Password Credentials grant.

    https://datatracker.ietf.org/doc/html/rfc6749#section-4.3.2
    """

    grant_type: str = GrantType.RESOURCE_OWNER_PASSWORD_CREDENTIALS
    username: str
    password: str
    scope: Optional[str] = None


class RefreshTokenAccessTokenRequest(AccessTokenRequest):
    """
    Request model for the access token request using a Refresh Token.

    https://datatracker.ietf.org/doc/html/rfc6749#section-6
    """

    grant_type: str = GrantType.REFRESH_TOKEN
    refresh_token: str
    scope: Optional[str] = None


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
    client_id: str


class DeviceAuthorizationRequest(BaseModel):
    """
    The Device Authorization Request model.

    https://datatracker.ietf.org/doc/html/rfc8628#section-3.1

    :ivar client_id: The client identifier.
    :ivar scope: The scope of the access request.
    """

    client_id: str
    scope: Optional[str] = None
