from __future__ import annotations

from abc import ABC, abstractmethod
from urllib.parse import urlparse

from crawler.models import RawPopupCandidate
from crawler.url_utils import is_allowed_domain


class BaseAdapter(ABC):
    domains: tuple[str, ...] = ()

    def matches(self, url: str) -> bool:
        host = (urlparse(url).hostname or "").lower()
        return any(is_allowed_domain(host, domain) for domain in self.domains)

    @abstractmethod
    def parse(self, html: str, source_url: str) -> list[RawPopupCandidate]:
        raise NotImplementedError
