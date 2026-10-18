# -*- coding: utf-8 -*-
"""Core parser for user_agent_py.

Only the standard library is used. The parser works in two passes:

  1. Split the User-Agent string on ";" and look for tokens of the form
     "name/version" or bare family names. This is the historical UA
     convention, e.g. "Mozilla/5.0 (Windows NT 10.0; Win64; x64)
     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36".
  2. Fall back to substring matching for families that do not follow the
     token convention (mobile Safari, some bots).

Because the UA format is deliberately human-readable and loosely specified,
we trade precision for predictability: the same string always yields the
same dict. We do NOT try to infer hardware model, screen size, or carrier —
that information is absent from the header and inventing it would be worse
than admitting we don't know.
"""

import re

USER_AGENT_PY_VERSION = "1.0.0"


# Each entry: family name, compiled regex.
# Order matters: we check the first match in order and stop. That lets us
# handle the common UA quirk where multiple engines are advertised in a
# single string (e.g. Chrome advertises both AppleWebKit and KHTML). We pick
# the most specific match the order is designed to surface.
_ENGINES = [
    ("Blink", re.compile(r"Chrome/([\d.]+)")),
    ("Trident", re.compile(r"Trident/([\d.]+)")),
    ("Gecko", re.compile(r"Gecko/[\d.]+|rv:[\d.]+")),
    ("WebKit", re.compile(r"AppleWebKit/[\d.]+")),
    ("KHTML", re.compile(r"KHTML")),
]

# Browser tokens, ordered. Netscape/Gecko-derived browsers must come before
# generic Safari; Chrome-based browsers must come before the Blink engine
# fallback. The regex captures a version after a slash, if present.
_BROWSERS = [
    ("Edge", re.compile(r"Edg(?:e|A|iOS)?/([\d.]+)")),
    ("Opera", re.compile(r"OPR/([\d.]+)")),
    ("Opera", re.compile(r"Opera[/ ]([\d.]+)")),
    ("Chrome", re.compile(r"(?:Chrome|CriOS)/([\d.]+)")),
    ("Firefox", re.compile(r"(?:Firefox|FxiOS)/([\d.]+)")),
    ("Safari", re.compile(r"Version/([\d.]+).*Safari")),
    ("Safari", re.compile(r"Safari/([\d.]+)")),
    ("Internet Explorer", re.compile(r"MSIE ([\d.]+)")),
    ("Internet Explorer", re.compile(r"Trident/[\d.]+;.*rv:([\d.]+)")),
]

# Operating systems. Windows NT versions are mapped to friendly names because
# the raw token is meaningless to most consumers (e.g. Windows NT 10.0 ==
# Windows 10/11). macOS versions are taken from the Darwin kernel version
# where available, because "Mac OS X 10_15_7" appears less reliably than the
# Darwin token.
_OS = [
    ("Windows", re.compile(r"Windows NT 10.0"), "10/11"),
    ("Windows", re.compile(r"Windows NT 6.3"), "8.1"),
    ("Windows", re.compile(r"Windows NT 6.2"), "8"),
    ("Windows", re.compile(r"Windows NT 6.1"), "7"),
    ("Windows", re.compile(r"Windows NT 6.0"), "Vista"),
    ("Windows", re.compile(r"Windows NT 5.1"), "XP"),
    ("Android", re.compile(r"Android ([\d.]+)"), None),
    ("Android", re.compile(r"Android"), ""),
    ("iOS", re.compile(r"iPhone OS ([\d_]+)"), None),
    ("iOS", re.compile(r"CPU OS ([\d_]+)"), None),
    ("macOS", re.compile(r"Mac OS X 10_([\d_]+)"), None),
    ("macOS", re.compile(r"Mac OS X ([\d.]+)"), None),
    ("macOS", re.compile(r"Macintosh"), ""),
    ("Chrome OS", re.compile(r"CrOS"), ""),
    ("Linux", re.compile(r"Linux"), ""),
]

# Device type is the loosest field. We distinguish mobile/tablet/desktop/
# bot/other by a small set of substring rules. This deliberately cannot tell
# an iPhone from an iPod touch; the UA header does not reliably carry that.
_DEVICES = [
    ("bot", re.compile(r"bot", re.IGNORECASE)),
    ("tablet", re.compile(r"iPad|Tablet|Silk-Accelerated", re.IGNORECASE)),
    ("mobile", re.compile(r"Mobile|Mobi|Android.*Mobile|iPhone", re.IGNORECASE)),
    ("desktop", re.compile(r"Windows NT|Macintosh|CrOS|Linux (x86_64|i686)")),
    ("mobile", re.compile(r"Android", re.IGNORECASE)),
]


def _empty_record():
    return {
        "browser": {"family": "", "version": ""},
        "engine": {"family": "", "version": ""},
        "operating_system": {"family": "", "version": ""},
        "device_type": {"family": "other", "version": ""},
    }


def _first_match(rules, ua):
    """Return the (family, version) of the first matching rule, or None."""
    for family, rx in rules:
        m = rx.search(ua)
        if m:
            version = m.group(1) if m.groups() else ""
            return family, version
    return None


def _match_os(ua):
    """OS rules carry an optional explicit version override. See _OS."""
    for family, rx, override in _OS:
        m = rx.search(ua)
        if m:
            if override is not None:
                version = override
            elif m.groups():
                version = m.group(1).replace("_", ".")
            else:
                version = ""
            return family, version
    return None


def _match_device(ua):
    for family, rx in _DEVICES:
        if rx.search(ua):
            return family, ""
    return "other", ""


def parse(user_agent_string):
    """Parse a User-Agent header string.

    Returns a dict with keys "browser", "engine", "operating_system",
    "device_type", each mapping to {"family": str, "version": str}.

    A missing family is the empty string; a missing version is the empty
    string. device_type family is one of "desktop", "mobile", "tablet",
    "bot", or "other". We never return None for any leaf value, so callers
    can index without guarding.
    """
    if not isinstance(user_agent_string, str):
        raise TypeError("user_agent_string must be str, got " + type(user_agent_string).__name__)
    if not user_agent_string.strip():
        return _empty_record()

    result = _empty_record()

    browser = _first_match(_BROWSERS, user_agent_string)
    if browser:
        result["browser"]["family"], result["browser"]["version"] = browser

    engine = _first_match(_ENGINES, user_agent_string)
    if engine:
        result["engine"]["family"], result["engine"]["version"] = engine

    os_match = _match_os(user_agent_string)
    if os_match:
        result["operating_system"]["family"], result["operating_system"]["version"] = os_match

    device_family, _ = _match_device(user_agent_string)
    result["device_type"]["family"] = device_family

    return result
