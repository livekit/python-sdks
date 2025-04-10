from __future__ import annotations

import sys
import atexit
import contextlib
import html
from IPython.core.display import HTML
from IPython.display import display
from importlib.resources import as_file, files

_resource_stack = contextlib.ExitStack()
atexit.register(_resource_stack.close)


def room_html(url: str, token: str, *, width: str, height: str) -> HTML:
    """
    Generate the HTML needed to embed a LiveKit room.

    Args:
        url (str): The LiveKit room URL.
        token (str): The LiveKit join token.

    Important:
        The returned HTML contains the provided `url` and `token` values directly.
        Avoid using sensitive tokens in public notebooks (e.g., tokens with long expiration times).
    """
    token_placeholder = "##livekit-token-placeholder##"
    url_placeholder = "##livekit-url-placeholder##"

    index_path = files("livekit.rtc.resources") / "jupyter-html" / "index.html"
    index_path = _resource_stack.enter_context(as_file(index_path))

    # turns out that directly replacing the URL/token is necessary, as Colab or Jupyter comms become
    # unreliable when the main thread is busy/blocked.
    # it also avoid the need to use --expose-app-in-browser when starting jupyter notebook
    html_text = index_path.read_text()
    html_text = html_text.replace(token_placeholder, token)
    html_text = html_text.replace(url_placeholder, url)

    IN_COLAB = "google.colab" in sys.modules

    # Colab output already runs inside an iframe, so we don’t need to create an additional one.
    # It also injects code into this iframe to handle microphone usage, so we need to preserve it.
    if not IN_COLAB:
        escaped_content = html.escape(html_text, quote=True)
        # the extra space in the iframe_html is to avoid IPython suggesting to use IFrame instead.
        # it isn't possible in our case, as we need to use srcdoc.
        html_text = (
            f' <iframe width="{width}" height="{height}" frameborder="0" '
            f'srcdoc="{escaped_content}"></iframe>'
        )

    return HTML(html_text)


def display_room(url: str, token: str, *, width: str = "100%", height: str = "110px") -> None:
    """
    Display a LiveKit room in a Jupyter notebook or Google Colab.

    Args:
        url (str): The LiveKit room URL.
        token (str): The LiveKit join token.

    Important:
        The rendered HTML will include the provided `url` and `token` in plain text.
        Avoid using sensitive tokens in public notebooks (e.g., tokens with long expiration times).
    """
    display(room_html(url, token, width=width, height=height))
