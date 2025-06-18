# `aiohttp-oauth2-client`: OAuth2 support for `aiohttp` client

This package adds support for OAuth 2.0 authorization to the `ClientSession` class of
the [`aiohttp`](https://docs.aiohttp.org/en/stable/) library.
It handles retrieving access tokens and injects them in the Authorization header of HTTP requests as a Bearer token.

**Features**:

* Ease of use
* Supported OAuth2 grants:
    * [Resource Owner Password Credentials](https://datatracker.ietf.org/doc/html/rfc6749#section-4.3)
    * [Client Credentials](https://datatracker.ietf.org/doc/html/rfc6749#section-4.4)
    * [Authorization Code (+ PKCE)](https://datatracker.ietf.org/doc/html/rfc6749#section-4.1)
    * [Device Code (+ PKCE)](https://datatracker.ietf.org/doc/html/rfc8628)
* Automatic (lazy) refresh of tokens
* Extensible code architecture

## Installation

The pacakge is available on [PyPi](https://pypi.org/project/aiohttp-oauth2-client) and can be installed using `pip`:

```shell
pip install aiohttp-oauth2-client
``` 

## Usage

Begin by importing the relevant modules, like the OAuth2 client middleware and grant. Also import `asyncio` for running async code:

```python
import asyncio
from aiohttp import ClientSession
from aiohttp_oauth2_client.middleware import OAuth2Middleware
from aiohttp_oauth2_client.grant.device_code import DeviceCodeGrant
```

Then create an `OAuth2Grant` and `OAuth2Middleware` object and perform a HTTP request to a protected resource. We use the
Device Code grant in this example:

```python
async def main():
    async with DeviceCodeGrant(
            token_url=TOKEN_URL,
            device_authorization_url=DEVICE_AUTHORIZATION_URL,
            client_id=CLIENT_ID,
            pkce=True
    ) as grant, ClientSession(middlewares=(OAuth2Middleware(grant),)) as client:
        async with client.get(PROTECTED_ENDPOINT) as response:
            assert response.ok
            print(await response.text())


asyncio.run(main())
```

The client and grant objects can be used as async context managers. This ensures the proper setup and cleanup of
associated resources.

### Grant configuration

This section provides an overview of the configuration options for each grant type.
Extra parameters can be provided, which will then be used in the authorization process.

#### Authorization code grant

The authorization code grant uses a web browser login to request an authorization code, which is then used to request an
access token.

##### Parameters

| Parameter           | Required | Description                 |
|---------------------|----------|-----------------------------|
| `token_url`         | Yes      | OAuth 2.0 Token URL         |
| `authorization_url` | Yes      | OAuth 2.0 Authorization URL | 
| `client_id`         | Yes      | client identifier           |
| `token`             | No       | OAuth 2.0 Token             | 
| `pkce`              | No       | use PKCE                    | 

##### Example

```python
from aiohttp import ClientSession
from aiohttp_oauth2_client.middleware import OAuth2Middleware
from aiohttp_oauth2_client.grant.authorization_code import AuthorizationCodeGrant

...

async with AuthorizationCodeGrant(
        token_url="https://sso.example.com/oauth2/token",
        authorization_url="https://sso.example.com/oauth2/auth",
        client_id="public",
        pkce=True
) as grant, ClientSession(middlewares=(OAuth2Middleware(grant),)) as client:
    ...
```

#### Client credentials grant

Use client credentials to obtain an access token.

##### Parameters

| Parameter       | Required | Description         |
|-----------------|----------|---------------------|
| `token_url`     | Yes      | OAuth 2.0 Token URL | 
| `client_id`     | Yes      | client identifier   |
| `client_secret` | Yes      | client secret       |
| `token`         | No       | OAuth 2.0 token     |

##### Example

```python
from aiohttp import ClientSession
from aiohttp_oauth2_client.middleware import OAuth2Middleware
from aiohttp_oauth2_client.grant.client_credentials import ClientCredentialsGrant

...

async with ClientCredentialsGrant(
        token_url="https://sso.example.com/oauth2/token",
        client_id="my-client",
        client_secret="top-secret"
) as grant, ClientSession(middlewares=(OAuth2Middleware(grant),)) as client:
    ...
```

#### Device code grant

Obtain user authorization on devices with limited input capabilities or lack a suitable browser to handle an interactive
log in procedure.
The user is instructed to review the authorization request on a secondary device, which does have the requisite input
and browser capabilities to complete the user interaction.

##### Parameters

| Parameter                  | Required | Description                        | 
|----------------------------|----------|------------------------------------|
| `token_url`                | Yes      | OAuth 2.0 Token URL                |
| `device_authorization_url` | Yes      | OAuth 2.0 Device Authorization URL |
| `client_id`                | Yes      | client identifier                  |
| `token`                    | No       | OAuth 2.0 Token                    | 
| `pkce`                     | No       | use PKCE                           |

##### Example

```python
from aiohttp import ClientSession
from aiohttp_oauth2_client.middleware import OAuth2Middleware
from aiohttp_oauth2_client.grant.device_code import DeviceCodeGrant

...

async with DeviceCodeGrant(
        token_url="https://sso.example.com/oauth2/token",
        device_authorization_url="https://sso.example.com/oauth2/auth/device",
        client_id="public",
        pkce=True
) as grant, ClientSession(middlewares=(OAuth2Middleware(grant),)) as client:
    ...
```

#### Resource owner password credentials grant

Use the username and password of the resource owner to obtain an access token.

##### Parameters

| Parameter   | Required | Description                    |
|-------------|----------|--------------------------------|
| `token_url` | Yes      | OAuth 2.0 Token URL            |
| `username`  | Yes      | username of the resource owner |
| `password`  | Yes      | password of the resource owner |
| `token`     | No       | OAuth 2.0 Token                |

##### Example

```python
from aiohttp import ClientSession
from aiohttp_oauth2_client.middleware import OAuth2Middleware
from aiohttp_oauth2_client.grant.resource_owner_password_credentials import ResourceOwnerPasswordCredentialsGrant

...

async with ResourceOwnerPasswordCredentialsGrant(
        token_url="https://sso.example.com/oauth2/token",
        username="username",
        password="password123",
        client_id="public"
) as grant, ClientSession(middlewares=(OAuth2Middleware(grant),)) as client:
    ...
```

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

### Build the docs

This repository uses Sphinx to generate documentation for the Python package.
To build the documentation, first install the required dependencies via the extra `docs`:

```shell
pip install -e .[docs]
```

Then go to the documentation directory and build the docs:

```shell
cd docs/
make html
```