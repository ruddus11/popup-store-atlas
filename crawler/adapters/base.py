from __future__ import annotations

from abc import ABC, abstractmethod
from urllib.parse import urlparse

from crawler.models import RawPopupCandidate


class BaseAdapter(ABC):
    domains: tuple[str, ...] = ()

    def matches(self, url: str) -> bool:
        host = urlparse(url).netloc.lower()
        return any(host.endswith(domain) for domain in self.domains)

    @abstractmethod
    def parse(self, html: str, source_url: str) -> list[RawPopupCandidate]:
        raise NotImplementedError

