---
"livekit-api": minor
---

Add a `token_source` option on `LiveKitAPI` that supplies a token for the claims of each call, in place of an API key and secret. Add `AccessToken.to_claims_json()`, which returns those claims as JSON.
