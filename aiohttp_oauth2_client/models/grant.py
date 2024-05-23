import enum


class GrantType(str, enum.Enum):
    """
    Enumeration of OAuth 2.0 grant types with their corresponding identifier.
    """

    REFRESH_TOKEN = "refresh_token"
    AUTHORIZATION_CODE = "authorization_code"
    RESOURCE_OWNER_PASSWORD_CREDENTIALS = "password"
    CLIENT_CREDENTIALS = "client_credentials"
    DEVICE_CODE = "urn:ietf:params:oauth:grant-type:device_code"
