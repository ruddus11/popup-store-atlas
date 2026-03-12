from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

from crawler.constants import ALLOWED_SOURCE_DOMAINS


def is_allowed_domain(host: str, domain: str) -> bool:
    normalized_host = host.lower().rstrip(".")
    normalized_domain = domain.lower().rstrip(".")
    return normalized_host == normalized_domain or normalized_host.endswith(f".{normalized_domain}")


def validate_source_url(
    url: str,
    allowed_domains: tuple[str, ...] = ALLOWED_SOURCE_DOMAINS,
) -> tuple[str | None, str | None]:
    try:
        parsed = urlsplit(url.strip())
    except ValueError:
        return None, "malformed_source_url"

    if parsed.scheme != "https":
        return None, "unsupported_source_scheme"

    if not parsed.netloc or parsed.username or parsed.password:
        return None, "invalid_source_host"

    host = (parsed.hostname or "").lower()
    if not host:
        return None, "invalid_source_host"

    if not any(is_allowed_domain(host, domain) for domain in allowed_domains):
        return None, "unsupported_source_domain"

    normalized_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path or "/", parsed.query, ""))
    return normalized_url, None
