from __future__ import annotations

import html
import re


def normalize_text(value: str) -> str:
    value = html.unescape(value)
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_heading(value: str) -> str:
    value = normalize_text(value)
    value = value.strip(" -:|()[]")
    return value
