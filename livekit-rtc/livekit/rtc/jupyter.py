from __future__ import annotations

import atexit
import sys
import contextlib
import os
from IPython.core.display import HTML, JSON
from IPython.display import display
from importlib.resources import as_file, files

_resource_stack = contextlib.ExitStack()
atexit.register(_resource_stack.close)


def room_html(url: str | None = None, token: str | None = None) -> HTML:
    """
    Display a LiveKit room in Jupyter or Google Colab.

    Args:
        url (str | None): The LiveKit room URL. If None, the function attempts
            to use the LIVEKIT_JUPYTER_URL environment variable in a local or
            Colab environment.
        token (str | None): The LiveKit join token. If None, the function
            attempts to use the LIVEKIT_JUPYTER_URL environment variable in a
            local or Colab environment.

    Returns:
        IPython.core.display.HTML: The HTML object that embeds the LiveKit room.

    Raises:
        ValueError: If both `url` and `token` are None and
            `LIVEKIT_JUPYTER_URL` is not set.
    """
    IN_COLAB = "google.colab" in sys.modules

    if url is None and token is None:
        if IN_COLAB:
            from google.colab import userdata

            LIVEKIT_JUPYTER_URL = userdata.get("LIVEKIT_JUPYTER_URL")
        else:
            LIVEKIT_JUPYTER_URL = os.environ.get("LIVEKIT_JUPYTER_URL")

        if not LIVEKIT_JUPYTER_URL:
            raise ValueError("LIVEKIT_JUPYTER_URL must be set (or url/token must be provided).")

    if IN_COLAB:
        from google.colab import output

        def create_join_token():
            return JSON({"url": url or "", "token": token or ""})

        output.register_callback("get_join_token", create_join_token)

    # Load the local HTML file that embeds the LiveKit client
    index_path = files("livekit.rtc.resources") / "jupyter-html" / "index.html"
    index_path = _resource_stack.enter_context(as_file(index_path))

    return HTML(index_path.read_text())


def display_room(url: str | None = None, token: str | None = None) -> None:
    """
    Display a LiveKit room in Jupyter or Google Colab.

    Args:
        url (str | None): The LiveKit room URL. If None, the function attempts
            to use the LIVEKIT_JUPYTER_URL environment variable in a local or
            Colab environment.
        token (str | None): The LiveKit join token. If None, the function
            attempts to use the LIVEKIT_JUPYTER_URL environment variable in a
            local or Colab environment.
    """
    display(room_html(url, token))
