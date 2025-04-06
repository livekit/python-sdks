# type: ignore
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
    IN_JUPYTER = "ipykernel" in sys.modules

    if IN_COLAB:
        from google.colab import output

        def get_join_token():
            return JSON({"url": url, "token": token})

        output.register_callback("get_join_token", get_join_token)
    elif IN_JUPYTER:
        from IPython import get_ipython

        ip = get_ipython()
        if ip and hasattr(ip, "kernel"):

            def token_comm_target(comm, open_msg):
                @comm.on_msg
                def handle_message(msg):
                    comm.send({"url": url, "token": token})

            ip.kernel.comm_manager.register_target("get_join_token_comm", token_comm_target)

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
