# user_agent_py

Extract browser, engine, operating system, and device type from User-Agent header strings using pattern matching. Zero third-party dependencies; standard library only.

```python
from user_agent_py import parse

result = parse("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
print(result["browser"]["family"])           # Chrome
print(result["browser"]["version"])          # 120.0.0.0
print(result["engine"]["family"])            # Blink
print(result["operating_system"]["family"])  # Windows
print(result["operating_system"]["version"]) # 10/11
print(result["device_type"]["family"])       # desktop
```

## Why this exists

A User-Agent header is the only signal most servers have for browser/OS segmentation, but the format is a free-text mishmash maintained by convention, not spec. Heavy parsers pull in large regex tables and, often, a dependency tree. This library trades completeness for predictability: the standard library only, a fixed rule list, and a return shape that never varies. If you need device-level hardware inference or carrier detection, this is not the right tool — that information is simply absent from the header, and inventing it would be worse than returning the empty string.

## The awkward edge

`device_type` cannot distinguish an iPhone from an iPod touch, because the header does not carry that distinction reliably. We return `"mobile"` for both. Likewise, `Windows NT 10.0` maps to `"10/11"` because the same token covers both Windows 10 and Windows 11; the header itself is identical. A missing field is the empty string `""`, not `None`, so you can index a leaf without guarding.
