##
# Project Title
#
# @file
# @version 0.1

.PHONY=flake8 black mypy lint types run debug

lint: flake8 black mypy

flake8:
	poetry run flake8 mitm_wifi

black:
	@poetry run black -- --check mitm_wifi --quiet

mypy:
	@poetry run mypy -p mitm_wifi --strict-optional

format:
	@poetry run black mitm_wifi

test:
	@poetry run pytest

types:
	@poetry run stubgen mitm_wifi

run:
	@sudo pipx run --no-cache --spec ./ mitm

debug:
	@sudo pipx run --no-cache --spec ./ mitm --verbose

# end
