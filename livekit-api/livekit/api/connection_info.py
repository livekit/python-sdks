import os


class ConnectionInfo:
    def __init__(self):
        self.url = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
        self.api_key = os.getenv("LIVEKIT_API_KEY")
        self.api_secret = os.getenv("LIVEKIT_API_SECRET")

        if not self.api_key or not self.api_secret:
            raise ValueError(
                "LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set")

    def websocket_url(self) -> str:
        if self.url.startswith("http"):
            return self.url.replace("http", "ws", 1)
        return self.url

    def http_url(self) -> str:
        if self.url.startswith("ws"):
            return self.url.replace("ws", "http", 1)
        return self.url
