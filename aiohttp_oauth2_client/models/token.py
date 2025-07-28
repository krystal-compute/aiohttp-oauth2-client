from __future__ import annotations

import time
from typing import Optional

from pydantic import BaseModel, model_validator, ConfigDict


class Token(BaseModel):
    """
    Token Response model.

    https://datatracker.ietf.org/doc/html/rfc6749#section-5.1
    """

    access_token: str
    """Access token issued by the authorization server"""

    token_type: str
    """Type of the token issued"""

    expires_in: Optional[int] = None
    """Lifetime in seconds of the access token"""

    refresh_token: Optional[str] = None
    """Refresh token, which can be used to obtain new access tokens"""

    scope: Optional[str] = None
    """Scope of the access token"""

    expires_at: int
    """Expiration time of the access token"""

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def _validate_expires_at(cls, data):
        """
        If the 'expires_at' field is not provided,
        it will be computed based on the current time and the 'expires_in' field.
        """
        if isinstance(data, dict):
            if "expires_at" not in data:
                data["expires_at"] = int(time.time()) + int(data["expires_in"])
        return data

    def is_expired(self, early_expiry: int = 30) -> bool:
        """
        Indicates whether the access token is expired.
        The early expiry parameter allows to have some margin on the token expiry time.

        :param early_expiry: early expiry in seconds
        :return: True if the access token is valid given the early expiry, False otherwise
        """
        if not self.expires_at:
            raise ValueError("No token expiration information")
        return self.expires_at - early_expiry < time.time()
