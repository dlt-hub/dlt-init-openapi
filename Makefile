# some useful commands for developing


# lint
lint:
	rm -rf tests/_local
	poetry run flake8 openapi_python_client tests
	poetry run mypy openapi_python_client tests
	poetry run black tests openapi_python_client --check
	poetry run isort black tests openapi_python_client --check --diff

# format the whole project
format: 
	rm -rf tests/_local
	poetry run isort black tests openapi_python_client
	poetry run black tests openapi_python_client

test:
	poetry run pytest tests 

# test without running all the original specs
test-fast:
	poetry run pytest tests -m "not slow"

# dev helpers
create-pokemon-pipeline:
	rm -rf pokemon-pipeline
	poetry run dlt-init init pokemon --url https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml --no-interactive

run-pokemon-pipeline:
	cd pokemon-pipeline && poetry run python pipeline.py