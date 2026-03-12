from crawler.adapters.base import BaseAdapter
from crawler.adapters.marieclaire import MarieClaireAdapter
from crawler.adapters.tistory import TistoryAdapter

ADAPTERS: list[BaseAdapter] = [
    MarieClaireAdapter(),
    TistoryAdapter(),
]

