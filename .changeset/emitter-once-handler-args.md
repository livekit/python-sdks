---
"livekit-rtc": patch
---

Pass `EventEmitter.once()` handlers only the arguments they accept, as `on()` does, and let `off()` remove a `once()` handler.
