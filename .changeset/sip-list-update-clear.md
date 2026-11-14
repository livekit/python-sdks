---
"livekit-api": patch
---

Keep `ListUpdate.clear` in the SIP `update_*_fields` helpers, so `ListUpdate(clear=True)` clears the list instead of failing the update.
