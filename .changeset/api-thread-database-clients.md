---
"livekit-api": patch
---

Add `LiveKitAPI.threads` (`create_thread`, `get_thread`, `list_threads`, `update_thread`, `delete_thread`, `get_thread_items`, `get_thread_tasks`) and `LiveKitAPI.databases` (`create_database`, `get_database`, `list_databases`, `delete_database`, `export_database`), served by the LiveKit Cloud Public API, with their request and response types exported from `livekit.api` (`CreateThreadRequest`, `Thread`, ...). The HTTP layer is generated from the vendored Public API OpenAPI spec (`livekit-api/public-api/generate.sh`).
