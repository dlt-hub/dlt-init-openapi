# some useful commands for developing


update-rest-api:
	poetry run python dlt_openapi/utils/update_rest_api.py


# lint
lint: update-rest-api
	rm -rf tests/_local
	poetry run flake8 dlt_openapi tests
	poetry run mypy dlt_openapi tests
	poetry run black tests dlt_openapi --check
	poetry run isort black tests dlt_openapi --check --diff

# format the whole project
format: update-rest-api
	rm -rf tests/_local
	poetry run isort black tests dlt_openapi
	poetry run black tests dlt_openapi

# all tests excluding the checks on e2e tests
test: update-rest-api
	poetry run python dlt_openapi/utils/update_rest_api.py
	poetry run pytest tests --ignore=tests/e2e

# test without running all the specs through a source
test-fast: update-rest-api
	poetry run pytest tests -m "not slow" --ignore=tests/e2e

# dev helpers
create-pokemon-pipeline:
	poetry run dlt-openapi init pokemon --url https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml --no-interactive

create-pokemon-pipeline-interactive:
	poetry run dlt-openapi init pokemon --url https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml

# e2e test helpers
create-e2e-pokemon-pipeline:
	poetry run dlt-openapi init pokemon --path tests/cases/e2e_specs/pokeapi.yml --global-limit 2 --no-interactive

run-pokemon-pipeline:
	cd pokemon-pipeline && poetry run python pipeline.py

check-pokemon-pipeline:
	poetry run pytest tests/e2e