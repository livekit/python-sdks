"""Smoke test: import the SDK and initialize the FFI library."""


def test_import_and_ffi_initialize():
    from livekit import rtc  # noqa: F401
    from livekit.rtc._ffi_client import FfiClient

    # accessing .instance triggers livekit_ffi_initialize
    assert FfiClient.instance is not None
