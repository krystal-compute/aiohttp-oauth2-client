from aiohttp_oauth2_client.models.response import ErrorResponse


class AuthError(Exception):
    """
    Auth error.
    """

    pass


class OAuth2Error(AuthError):
    """
    Error in the OAuth 2.0 authorization process.
    """

    def __init__(self, response: ErrorResponse):
        self.response = response
        message = (
            f"{response.error}: {response.error_description}"
            if response.error_description
            else response.error
        )
        super().__init__(message)

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.response.error}">'
