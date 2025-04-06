import atexit
import contextlib
import os
from IPython.core.display import HTML
from importlib.resources import as_file, files

_resource_stack = contextlib.ExitStack()
atexit.register(_resource_stack.close)


def display_room() -> HTML:
    try:
        from google.colab import secrets

        LIVEKIT_JUPYTER_URL = secrets.get("LIVEKIT_JUPYTER_URL")
    except ImportError:
        LIVEKIT_JUPYTER_URL = os.environ.get("LIVEKIT_JUPYTER_URL")

    if not LIVEKIT_JUPYTER_URL:
        raise ValueError(
            "LIVEKIT_JUPYTER_URL must be set via Google Colab secrets or as an environment variable."
        )

    index_path = files("livekit.rtc.resources") / "jupyter-html" / "index.html"
    index_path = _resource_stack.enter_context(as_file(index_path))
    html_text = index_path.read_text()

    return HTML(html_text)
