import asyncio
import time
from typing import Optional, Union
from yarl import URL

from aiohttp_oauth2_client.grant.common import OAuth2Grant
from aiohttp_oauth2_client.models.request import (
    DeviceAuthorizationRequest,
    DeviceAccessTokenRequest,
)
from aiohttp_oauth2_client.models.response import DeviceAuthorizationResponse


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
        self.authorization_request = DeviceAuthorizationRequest.model_validate(kwargs)

    async def _fetch_token(self):
        time_start = time.time()
        device_code_url = self.authorization_url / "device"
        async with self.session.post(
            url=device_code_url,
            data=self.authorization_request.model_dump(exclude_none=True),
        ) as response:
            device_authorization = DeviceAuthorizationResponse.model_validate(
                await response.json()
            )
        token_request_data = DeviceAccessTokenRequest(
            device_code_url=device_authorization.device_code, **self.kwargs
        )
        # TODO show message to user

        complete = False
        while (
            not complete
            and not time.time() > time_start + device_authorization.expires_in
        ):
            await asyncio.sleep(device_authorization.interval)
            try:
                token = await self.execute_token_request(token_request_data)
                if token:
                    complete = True
                    return token
            except Exception:
                pass
