import os
import hashlib
import base64


class PKCE:
    """
    Proof Key for Code Exchange by OAuth Public Clients

    Generates code verifier and code challenge.

    https://datatracker.ietf.org/doc/html/rfc7636
    """

    def __init__(self):
        self.code_verifier: bytes = PKCE.create_code_verifier()
        self.code_challenge_method: str = "S256"
        self.code_challenge: bytes = PKCE.create_code_challenge(self.code_verifier)

    @staticmethod
    def create_code_verifier() -> bytes:
        return base64.urlsafe_b64encode(os.urandom(64)).rstrip(b"=")

    @staticmethod
    def create_code_challenge(code_verifier: bytes) -> bytes:
        digest = hashlib.sha256(code_verifier).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=")
