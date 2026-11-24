---
"livekit-rtc": patch
---

`EventEmitter.emit` logs a `TypeError` raised inside a handler instead of re-raising it. An event with too few arguments for the handler still raises.
