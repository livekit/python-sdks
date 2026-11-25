---
"livekit-api": patch
---

Apply a timeout to every API request. Requests previously ignored the session timeout and waited indefinitely, so a host that accepted the connection but never answered blocked the call and prevented region failover. `LiveKitAPI(timeout=...)` now also applies when a session is supplied by the caller, giving API calls a deadline without changing the timeout of other traffic sharing that session.
