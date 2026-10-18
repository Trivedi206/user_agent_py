# -*- coding: utf-8 -*-
"""user_agent_py — a small, dependency-free User-Agent header parser.

What this exports:
    parse(user_agent_string) -> dict
        Keys returned: "browser", "engine", "operating_system", "device_type".
        Each value is a dict of the form {"family": str, "version": str},
        where version may be "" if it could not be determined.
    USER_AGENT_PY_VERSION
        The library version string.

Design choice: we attempt to preserve version information when it appears in
the standard ";name/version" tokens that most User-Agent strings emit. Some
fields (notably device type) rarely carry a version in practice, so their
version is returned as the empty string rather than None, to keep the value
shape uniform across all four fields.
"""

from .core import parse, USER_AGENT_PY_VERSION

__all__ = ["parse", "USER_AGENT_PY_VERSION"]
