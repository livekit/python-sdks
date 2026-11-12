---
"livekit-rtc": minor
---

Add `PrewarmedConnection` and `RoomOptions.prewarmed_connection` to open the signalling TCP/TLS connection ahead of `Room.connect`, so the connect only performs the WebSocket upgrade.
