# dlt-openapi
`dlt-openapi` generates [`dlt`](https://dlthub.com/docs) pipelines from OpenAPI 3.x documents/specs using the [`dlt` `rest_api` `verified source`](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api). If you do not know `dlt` or our `verified sources`, please read:

* [Getting started](https://dlthub.com/docs/getting-started) to learn the `dlt` basics
* [dlt rest_api](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api) to learn how our `rest_api` source works

> This generator does not support OpenAPI 2.x FKA Swagger. If you need to use an older document, try upgrading it to
version 3 first with one of many available converters.


## Prior work
This project started as a fork of [openapi-python-client](https://github.com/openapi-generators/openapi-python-client). Pretty much all parts are heavily changed or completely replaced, but some lines of code still exist and we like to acknowledge the many good ideas we got from the original project :)


## Features
The dlt-openapi generates code from an OpenAPI spec that you can use to extract data from a `rest_api` into any [`destination`](https://dlthub.com/docs/dlt-ecosystem/destinations/) (e.g. Postgres, BigQuery, Redshift...) `dlt` supports.

Features include

* [Pagination](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api#pagination) discovery
* Primary key discovery
* Endpoint relationship mapping into `dlt` [`transformers`](https://dlthub.com/docs/general-usage/resource#process-resources-with-dlttransformer) (e.g. /users/ -> /user/{id})
* Payload JSON path [data selector](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api#data-selection) discovery for nested results
* [Authentication](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api#authentication) discovery

## Setup

You will need Python 3.9 installed, as well as [`poetry`](https://python-poetry.org/docs/) to install dependencies.

```console
# 1. Checkout this repository locally
$ git clone git@github.com:dlt-hub/dlt-openapi.git

# 2. Install required poetry dependencies
$ poetry install

# 3. Start the poetry shell
$ poetry shell
```

## Basic Usage

Let's create an example pipeline from the [PokeAPI spec](https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml). You can point to any other OpenAPI Spec instead if you like.

```console
# 1. Run the generator with the dlt-openapi init command:
$ dlt-openapi init pokemon --url https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml

# 2. You can now pick the endpoints you need from the popup

# 3. After selecting your pokemon endpoints and hitting Enter, your pipeline will be rendered

# 4. Go to the created pipeline folder and run your pipeline
$ cd pokemon-pipeline
$ PROGRESS=enlighten python pipeline.py # we use enlighten for a nice progress bar :)

# 5. Print the pipeline info to console to see what got loaded
$ dlt pipeline pokemon_pipeline info

# 6. You can now also install streamlit to see a preview of the data
$ pip install pandas streamlit
$ dlt pipeline pokemon_pipeline show
```

## What will be created?
When you run the `init` command above, the following files will be generated:

* `./pokemon-pipeline` - a folder containing the full project.
* `./pokemon-pipeline/pipeline.py` - a file which you can execute to run your pipeline.
* `./pokemon-pipeline/pokemon/__init__.py` - a file that contains the generated code to connect to the PokeApi, you can inspect this file and manually change it to your liking or to fix incorrectly generated results.
* `./pokemon-pipeline/.dlt` - a folder with the `config.toml`. You can add your `secrets.toml` with credentials here.
* `./pokemon-pipeline/rest_api` -  a folder that contains the rest_api source from our verified sources.

> If you re-generate your pipeline, you will be prompted to continue if this folder exists. If you select yes, all generated files will be overwritten. All other files you may have created will remain in this folder.

## CLI commands

```console
$ dlt-init [OPTIONS] COMMAND [ARGS]...
# example:
$ dlt-init init pokemon --path ./path/to/my_spec.yml
```

**Options**:

- `--version`: Print the version and exit [default: False]
- `--help`: Show this message and exit.

**Commands**:

- `init`: Generate a new `dlt` `rest_api` `source`

### `dlt-openapi init`

Generate a new `dlt` `rest_api` `source`

**Usage**:

```console
$ dlt-openapi init pokemon --path ./path/to/my_spec.yml
```

**Options**:

- `--url TEXT`: A url to read the OpenAPI JSON or YAML file from
- `--path PATH`: A path to read the OpenAPI JSON or YAML file from locally
- `--output-path PATH`: A path to render the output to
- `--config PATH`: Path to the config file to use (see below)
- `--no-interactive`: Skip endpoint selection and render all paths of the OpenAPI spec.
- `--loglevel`: Set logging level for stdout output, defaults to 20 (INFO).
- `--help`: Show this message and exit.

## Config options
You can pass a path to a config file with the `--config PATH` argument. To see available config values, go to https://github.com/dlt-hub/dlt-openapi/blob/master/dlt_openapi/config.py and read the information below each field on the `Config` class.

The config file can be supplied as json or yaml dictionary. For example to change the package name, you can create a yaml file:

```yaml
# config.yml
package_name: "other_package_name"
```

And use it with the config argument:

```console
$ dlt-openapi init pokemon --url ... --config config.yml
```

## Implementation notes
* OAuth Authentication currently is not natively supported, you can supply your own
* Per endpoint authentication currently is not supported by the generator, only the first globally set securityScheme will be applied. You can add your own per endpoint if you need to.
