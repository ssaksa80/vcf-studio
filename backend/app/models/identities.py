"""DNS identity normalization shared by blueprint fields."""
import re

_LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", re.ASCII)


def normalize_fqdn(value: str) -> str:
    name = value.strip().lower().removesuffix(".")
    labels = name.split(".")
    if len(name) > 253 or len(labels) < 2 or not all(_LABEL.fullmatch(label) for label in labels):
        raise ValueError("Use a fully qualified ASCII DNS name with valid labels")
    if labels[-1].isdigit():
        raise ValueError("Use a DNS name, not an IP address")
    return name
