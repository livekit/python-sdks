---
"livekit-api": patch
---

Add `LiveKitAPI.threads` and `LiveKitAPI.databases`: agent threads (create, get, list, update, delete, items, tasks) and agent databases (create, get, list, delete, export), served by the LiveKit Cloud Public API. The HTTP layer is generated from the vendored Public API OpenAPI spec (`livekit-api/public-api/generate.sh`).
