"""Neutralise attacker-controlled alert text before it reaches an LLM prompt.

Every scalar in an alert (signature, addresses, protocol, source) and the raw
event blob originate from the sensor, i.e. from whoever generated the traffic.
A crafted Suricata rule name or HTTP header carrying ``\\n\\nIgnore the above
instructions`` is a prompt-injection payload, so the prompt builders route
those values through here first.

Newlines and control characters are the payload's delivery mechanism — without
them injected text cannot pose as a new instruction block — so they are folded
to spaces rather than dropped, and every field is length-bounded.
"""

from __future__ import annotations

#: Long enough for any legitimate IDS signature; short enough that a padded
#: payload cannot push the real instructions out of the model's attention.
FIELD_MAX_CHARS = 300


def scrub_field(value: object, max_chars: int = FIELD_MAX_CHARS) -> str:
    """One prompt-safe line: no control characters, no newlines, bounded."""
    text = "" if value is None else str(value)
    cleaned = "".join(" " if ch < " " or ch == "\x7f" else ch for ch in text)
    cleaned = " ".join(cleaned.split())
    if len(cleaned) > max_chars:
        cleaned = cleaned[: max_chars - 1] + "…"
    return cleaned


def scrub_block(value: object, max_chars: int) -> str:
    """Same guarantees as :func:`scrub_field` for a larger excerpt."""
    return scrub_field(value, max_chars)


__all__ = ["FIELD_MAX_CHARS", "scrub_block", "scrub_field"]
