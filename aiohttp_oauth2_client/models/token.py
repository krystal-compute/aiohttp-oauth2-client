from __future__ import annotations

import time
from typing import Optional

from pydantic import BaseModel, model_validator, ConfigDict


class Token(BaseModel):
    """
    Token Response model.

    https://datatracker.ietf.org/doc/html/rfc6749#section-5.1

    :ivar access_token: The access token issued by the authorization server.
    :ivar token_type: The type of the token issued.
    :ivar expires_in: The lifetime in seconds of the access token.
    :ivar refresh_token: The refresh token, which can be used to obtain new access tokens.
    :ivar scope: The scope of the access token.
    :ivar expires_at: The expiration time of the access token.
    """

    access_token: str
    token_type: str
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    expires_at: int

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def validate_expires_at(cls, data):
        if isinstance(data, dict):
            if "expires_at" not in data:
                data["expires_at"] = int(time.time()) + data["expires_in"]
        return data

    def is_expired(self, early_expiry: int = 30) -> bool:
        if not self.expires_at:
            raise ValueError("No token expiration information")
        return self.expires_at - early_expiry < time.time()
