import atexit
import contextlib
from IPython.core.display import HTML
from importlib.resources import as_file, files

_resource_stack = contextlib.ExitStack()
atexit.register(_resource_stack.close)


def display_room() -> HTML:
    index_path = files("livekit.rtc.resources") / "jupyter-html" / "index.html"
    index_path = _resource_stack.enter_context(as_file(index_path))
    return HTML(index_path.read_text())
