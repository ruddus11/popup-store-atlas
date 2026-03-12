PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
CSV_PATH ?= data/interim/popup_stores.csv

.PHONY: install-python init-db crawl load-csv run-api frontend-install frontend-dev test

install-python:
	$(PIP) install -r requirements.txt

init-db:
	bash infra/scripts/init_db.sh

crawl:
	$(PYTHON) -m crawler.crawl --config crawler/config/seed_urls.json --output $(CSV_PATH)

load-csv:
	$(PYTHON) -m backend.load_csv --csv $(CSV_PATH)

run-api:
	$(PYTHON) -m uvicorn backend.app.main:app --reload

frontend-install:
	npm --prefix frontend install

frontend-dev:
	npm --prefix frontend run dev

test:
	$(PYTHON) -m pytest

