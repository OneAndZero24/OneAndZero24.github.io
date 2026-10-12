# Convenience targets for the website, publication sync, and CV generation.
# The venv is detected automatically when it exists (see README).

PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
HUGO ?= hugo

.PHONY: all sync sync-online cv site serve clean

all: sync cv site

## Merge the cached Scholar data with the manual overrides (no network).
sync:
	$(PYTHON) scripts/sync_publications.py --offline

## Fetch from Google Scholar, then merge. Requires `scholarly` or SERPAPI_API_KEY.
sync-online:
	$(PYTHON) scripts/sync_publications.py

## Regenerate cv/cv.tex and compile static/cv.pdf from the data files.
cv:
	$(PYTHON) scripts/generate_cv.py

## Build the site into public/.
site:
	$(HUGO) --minify

## Local development server at http://localhost:1313/.
serve:
	$(HUGO) server -M --disableFastRender

clean:
	rm -rf public resources .hugo_build.lock
