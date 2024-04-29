# some useful commands for developing


# lint
lint:
	flake8 openapi_python_client tests
	mypy openapi_python_client tests
	black . --check

# format the whole project
format: 
	black .

test:
	pytest tests

# dev helpers
create-pokemon-pipeline:
	rm -rf pokemon-pipeline
	dlt-init init pokemon --url https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml --no-interactive

