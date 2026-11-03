---
"livekit-rtc": patch
---

Create the shared `FfiClient` under a lock, so rooms connected from several threads at once no longer lose their connect callback and panic the process.
