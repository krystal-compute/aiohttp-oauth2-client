import asyncio
import time
from typing import Optional, Union
from yarl import URL

from aiohttp_oauth2_client.grant.common import OAuth2Grant, GrantType


class DeviceCodeGrant(OAuth2Grant):
    def __init__(
        self,
        token_url: Union[str, URL],
        authorization_url: Union[str, URL],
        token: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(token_url, token, **kwargs)
        self.authorization_url = URL(authorization_url)

    async def fetch_token(self):
        time_start = time.time()
        device_code_url = self.authorization_url / "device"
        response = await self.session.post(url=device_code_url, data=self.kwargs).json()
        polling_interval = int(response.get("interval", 5))
        expires_in = int(response["expires_in"])
        device_code = response["device_code"]
        data = dict(
            grant_type=GrantType.DEVICE_CODE, device_code=device_code, **self.kwargs
        )
        # TODO show message to user

        complete = False
        while not complete and not time.time() > time_start + expires_in:
            await asyncio.sleep(polling_interval)
            try:
                token = self.execute_token_request(data)
                if token:
                    complete = True
                    self.token = token
            except Exception:
                pass
