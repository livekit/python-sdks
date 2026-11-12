---
"livekit-rtc": patch
---

Return `VideoFrame.get_plane()` planes as views that keep the frame's buffer alive and stay read-only for a frame built from `bytes`.
