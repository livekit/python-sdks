---
"livekit-rtc": patch
---

`AudioSource.clear_queue` also stops a `capture_frame` in flight: a frame longer than the queue no longer keeps playing after a clear.
