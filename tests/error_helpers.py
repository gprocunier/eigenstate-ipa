"""Test helpers for robust exception assertions across ansible-core versions."""


def exception_text(exc):
    """Return a stable message for Ansible-style exceptions."""

    message = getattr(exc, "_message", None)
    if message:
        return str(message)

    args = getattr(exc, "args", ())
    if args:
        return " ".join(str(arg) for arg in args if arg is not None)

    try:
        return str(exc)
    except Exception:
        return repr(exc)
