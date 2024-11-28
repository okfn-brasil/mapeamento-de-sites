SOURCE_DIR := ./resultados/brutos
OUTPUT_DIR := ./resultados/tratados
FINAL_DATA_DIR := ./resultados

compile:
	pip-compile --upgrade --no-annotate --allow-unsafe --generate-hashes requirements.in; \
	pip-compile --upgrade --no-annotate --allow-unsafe --generate-hashes requirements-dev.in

run_spider:
	scrapy crawl $(SPIDER) --logfile=$(SPIDER).log

normalize:
	SOURCE_DIR=$(SOURCE_DIR) OUTPUT_DIR=$(OUTPUT_DIR) FINAL_DATA_DIR=$(FINAL_DATA_DIR) python3 normalize_results.py

run_all:
	make run_spider SPIDER=adiarios_v1
	make run_spider SPIDER=doem

	make normalize