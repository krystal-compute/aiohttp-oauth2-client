from __future__ import annotations

import time


class Token(dict):
    def __init__(self, seq, **kwargs):
        super().__init__(seq, **kwargs)
        if not self.expires_at:
            self.expires_at = int(time.time()) + self["expires_in"]
        if self.refresh_token and not self.refresh_expires_at:
            self.refresh_expires_at = int(time.time()) + self["refresh_expires_in"]

    @property
    def access_token(self) -> str:
        return self.get("access_token")

    @property
    def refresh_token(self) -> str:
        return self.get("refresh_token")

    @property
    def expires_at(self) -> int:
        return self.get("expires_at")

    @expires_at.setter
    def expires_at(self, value: int):
        self["expires_at"] = value

    @property
    def refresh_expires_at(self):
        return self.get("refresh_expires_at")

    @refresh_expires_at.setter
    def refresh_expires_at(self, value: int):
        self["refresh_expires_at"] = value

    @property
    def score(self) -> str:
        return self.get("scope")

    def is_expired(self, early_expiry: int = 30) -> bool:
        if not self.expires_at:
            raise ValueError("No token expiration information")
        return self.expires_at - early_expiry < time.time()
