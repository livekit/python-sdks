# LiveKit Server APIs

Access LiveKit server APIs and generate access tokens.

See https://docs.livekit.io/reference/server/server-apis for more information.

## Authentication

Every request to the server APIs is authenticated. `LiveKitAPI` supports two modes:

- **API key & secret** — recommended for backend use. The SDK signs a short-lived token per request from your key and secret. Keep your API secret on the server; never ship it to a client.
- **Access token** — for client-side use where the API secret must not be exposed. Pass a pre-signed [access token](https://docs.livekit.io/home/get-started/authentication/) that already carries the grants for the operations you'll perform; the SDK sends it verbatim.

```python
from livekit import api

# API key & secret: set LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET,
# then construct with no arguments...
lkapi = api.LiveKitAPI()

# ...or pass any of them explicitly to override the corresponding env var:
lkapi = api.LiveKitAPI("https://my.livekit.host", api_key="api-key", api_secret="api-secret")

# Pre-signed access token (client-side): with LIVEKIT_URL set, pass just the token:
lkapi = api.LiveKitAPI.with_token("a-pre-signed-token")
```

The url and credentials fall back to the `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, and `LIVEKIT_TOKEN` environment variables. Values you pass explicitly take precedence; the environment variables are used only as a fallback for arguments you omit — an ambient `LIVEKIT_TOKEN`, for example, won't override an explicitly-provided API key and secret.

