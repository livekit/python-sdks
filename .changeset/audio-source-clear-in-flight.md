---
"livekit-rtc": patch
---

`AudioSource.clear_queue` stops a `capture_frame` in flight: a frame longer than the queue no longer keeps playing after a clear, and a capture right after a clear no longer fails.
