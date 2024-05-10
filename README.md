# dlt-openapi
`dlt-openapi` generates [dlt](https://dlthub.com/docs) pipelines from OpenAPI 3.x documents using the [dlt rest_api verified source](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api). If you do not know dlt or our verified sources, please read:

* [Getting started](https://dlthub.com/docs/getting-started) to learn the dlt basics
* [dlt rest_api](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api) to learn how our rest api source works

> This generator does not support OpenAPI 2.x FKA Swagger. If you need to use an older document, try upgrading it to
version 3 first with one of many available converters.


## Prior work
This project is a heavily updated and changed fork of [openapi-python-client](https://github.com/openapi-generators/openapi-python-client). 


## Features
The dlt-openapi generates code from an openap spec that you can use to extract data from a rest api into any [destination](https://dlthub.com/docs/dlt-ecosystem/destinations/) (e.g. postgres, bigquery, redshift...) dlt supports.

Features include

* Pagination discovery
* Primary key discovery
* Endpoint relationship mapping into dlt transformers (e.g. /users/ -> /user/{id})
* Payload json path discovery for nested results
* Authentication discovery

## Setup

1. Checkout this repository locally
```console
$ git clone git@github.com:dlt-hub/dlt-openapi.git
```

2. Init git submodules
On fist use of the repo, fetch the **rest api** sources after checking out:
```console
$ git submodule update --init --recursive
```

	> On subsequent uses, to get the most up to date source:
	```
	git submodule update --recursive --remote
	```

3. You need [`poetry`](https://python-poetry.org/docs/) to install dependencies
```console
$ poetry install
$ poetry shell
```

## Basic Usage

Here we create an example pipeline from the [PokeAPI spec](https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml). You can point to any other OpenApi Spec instead if you like.

1. Run the generator with the dlt-openapi init command:

```console
$ dlt-openapi init pokemon --url https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml
```

2. After executing of the command, you can pick the endpoints that you want to add to your source and then load with the pipeline. The endpoints are grouped by returned data type (table) and ordered by centrality (a measure how many other tables, the given table links to):

```
? Which resources would you like to generate? (Use arrow keys to move, <space> to select, <a> to toggle, <i> to invert)
 
PokemonSpecies endpoints:

   ○ pokemon_species_list /api/v2/pokemon-species/
 » ○ pokemon_species_read /api/v2/pokemon-species/{id}/
 
EvolutionChain endpoints:

   ○ evolution_chain_list /api/v2/evolution-chain/
   ○ evolution_chain_read /api/v2/evolution-chain/{id}/
```

3. Pick your endpoints and press **ENTER** to generate pipeline. Now you are ready to load data.

4. Enter the `pokemon-pipeline` folder and execute the `pipeline.py` script. This will load your endpoints to local `duckdb`. Below we use `enlighten` to show some fancy progress bars:
```console
$ cd pokemon-pipeline
$ PROGRESS=enlighten python pipeline.py
```

5. Inspect the pipeline to see what got loaded
```console
$ dlt pipeline pokemon_pipeline info

Found pipeline pokemon_pipeline in /home/rudolfix/.dlt/pipelines
Synchronized state:
_state_version: 2
_state_engine_version: 2
pipeline_name: pokemon_pipeline
dataset_name: pokemon_data
default_schema_name: pokemon
schema_names: ['pokemon']
destination: dlt.destinations.duckdb

Local state:
first_run: False
_last_extracted_at: 2023-06-12T11:50:16.171872+00:00

Resources in schema: pokemon
pokemon_species_read with 8 table(s) and 0 resource state slot(s)

Working dir content:
Has 1 completed load packages with following load ids:
1686570616.17882

Pipeline has last run trace. Use 'dlt pipeline pokemon_pipeline trace' to inspect
```

8. Launch the streamlit app to preview the data (we copy a streamlit config to make it work on codespaces)
```console
$ cp -r ../.streamlit .
$ pip install pandas streamlit
$ dlt pipeline pokemon_pipeline show
```

## What You Get
When you run the command above, following files will be generated:

* A `./pokemon-pipeline` a folder containing the full project.
* A file `./pokemon-pipeline/pokemon/__init__.py` which contains the generated code to connect to the PokeApi, you can inspect this file and manually change it to your liking or to fix incorrectly generated results.
3. A file `./pokemon-pipeline/pipeline.py` which you can execute to run your pipeline.
5. `./pokemon-pipeline/.dlt` folder with the `config.toml`

## Cli commands

```console
$ dlt-init [OPTIONS] COMMAND [ARGS]...
# e.g.: dlt-init init pokemon --url https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml

```

**Options**:

- `--version`: Print the version and exit [default: False]
- `--help`: Show this message and exit.

**Commands**:

- `generate`: Generate a new OpenAPI Client library
- `update`: Update an existing OpenAPI Client library

### `dlt-openapi init`

Generate a new dlt source

**Usage**:

```console
$ openapi-python-client generate [OPTIONS]
```

**Options**:

- `--url TEXT`: A URL to read the JSON from
- `--path PATH`: A path to the JSON file
- `--config PATH`: Path to the config file to use (see below)
- `--help`: Show this message and exit.

## Config options
You can pass a path to a config file with the `--config PATH` argument. Config values include:

TODO...