CSV_HEADERS = [
    "name",
    "address",
    "start_date",
    "end_date",
    "source_url",
    "source_domain",
    "collected_at",
]

REJECTED_HEADERS = [
    "reason",
    "name",
    "address",
    "raw_period",
    "source_url",
    "source_domain",
]

ALLOWED_REGION_PREFIXES = (
    "서울",
    "서울특별시",
    "경기",
    "경기도",
    "충북",
    "충청북도",
    "충남",
    "충청남도",
    "대전",
    "대전광역시",
)

ALLOWED_SOURCE_DOMAINS = (
    "ehyundai.com",
    "marieclairekorea.com",
    "tistory.com",
)

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
)
