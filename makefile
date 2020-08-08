.PHONY: web
web:
	python3 -m tempmon.web

.PHONY: db
db:
	python3 -m tempmon.db

.PHONY: collector
collector:
	python3 -m tempmon.collector
