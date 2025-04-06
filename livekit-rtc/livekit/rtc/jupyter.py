from __future__ import annotations

import atexit
import sys
import contextlib
from IPython.core.display import HTML, JSON
from IPython.display import display
from importlib.resources import as_file, files

_resource_stack = contextlib.ExitStack()
atexit.register(_resource_stack.close)


def room_html(url: str, token: str) -> HTML:
    IN_COLAB = "google.colab" in sys.modules

    if IN_COLAB:
        from google.colab import output

        def get_join_token():
            return JSON({"url": url, "token": token})

        output.register_callback("get_join_token", get_join_token)

    index_path = files("livekit.rtc.resources") / "jupyter-html" / "index.html"
    index_path = _resource_stack.enter_context(as_file(index_path))
    return HTML(index_path.read_text())


def display_room(url: str, token: str) -> None:
    """
    Display a LiveKit room in Jupyter or Google Colab.

    Args:
        url (str): The LiveKit room URL.
        token (str): The LiveKit join token.
    """
    display(room_html(url, token))
