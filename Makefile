# some useful commands for developing


# lint
lint:
	rm -rf tests/_local
	poetry run flake8 dlt_openapi tests
	poetry run mypy dlt_openapi tests
	poetry run black tests dlt_openapi --check
	poetry run isort black tests dlt_openapi --check --diff

# format the whole project
format: 
	rm -rf tests/_local
	poetry run isort black tests dlt_openapi
	poetry run black tests dlt_openapi

test:
	poetry run pytest tests 

# test without running all the original specs
test-fast:
	poetry run pytest tests -m "not slow"

# dev helpers
create-pokemon-pipeline:
	poetry run dlt-openapi init pokemon --url https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml --no-interactive

create-pokemon-pipeline-interactive:
	poetry run dlt-openapi init pokemon --url https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml

run-pokemon-pipeline:
	cd pokemon-pipeline && poetry run python pipeline.py