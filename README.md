# aiohttp-oauth2-client: OAuth2 support for `aiohttp` client
This package adds support for OAuth 2.0 authorization to the `ClientSession` class of the `aiohttp` library.
It handles retrieving access tokens and injects them in the Authorization header of HTTP requests as a Bearer token.

**Features**:
* Supported OAuth2 grants:
  * [Resource Owner Password Credentials](https://datatracker.ietf.org/doc/html/rfc6749#section-4.3)
  * [Client Credentials](https://datatracker.ietf.org/doc/html/rfc6749#section-4.4)
  * [Authorization Code (+ PKCE)](https://datatracker.ietf.org/doc/html/rfc6749#section-4.1)
  * [Device Code (+ PKCE)](https://datatracker.ietf.org/doc/html/rfc8628)
* Automatic (lazy) refresh of tokens
* Extensible code architecture


## Installation
```shell
pip install aiohttp-oauth2-client
``` 

## Usage
Begin by importing the relevant modules, like the OAuth2 client and grant. Also import `asyncio` for running async code:
```python
import asyncio
from aiohttp_oauth2_client.client import OAuth2Client
from aiohttp_oauth2_client.grant.device_code import DeviceCodeGrant
```

Then create an `OAuth2Grant` and `OAuth2Client` object and perform a HTTP request to a protected resource. We use the Device Code grant in this example:
```python
async def main():
    async with DeviceCodeGrant(
            token_url=TOKEN_ENDPOINT,
            device_authorization_url=DEVICE_AUTHORIZATION_ENDPOINT,
            client_id=CLIENT_ID,
            pkce=True
    ) as grant, OAuth2Client(grant) as client:
        async with client.get(PROTECTED_ENDPOINT) as response:
            assert response.ok
            print(await response.text())

asyncio.run(main())
```

For more advanced options and a complete overview of the available OAuth2 grants and their configuration, see the documentation.

## Development
To start developing on this project, you should install all needed dependencies for running and testing the code:
```shell
pip install -e .[dev]
```

This will also install linting and formatting tools, which can be automatically executed when you commit using Git. 
To set up pre-commit as a Git hook, run:
```shell
pre-commit install
```

You can also run the pre-commit checks manually with the following command:
```shell
pre-commit run --all-files
```