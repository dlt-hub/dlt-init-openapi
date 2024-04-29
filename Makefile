# some useful commands for developing

create-pokemon-pipeline:
	rm -rf pokemon-pipeline
	dlt-init init pokemon --url https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml
