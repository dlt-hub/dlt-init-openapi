# dlt-init-openapi
`dlt-init-openapi` generates [`dlt`](https://dlthub.com/docs) pipelines from OpenAPI 3.x documents/specs using the [`dlt` `rest_api` `verified source`](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api). If you do not know `dlt` or our `verified sources`, please read:

* [Getting started](https://dlthub.com/docs/getting-started) to learn the `dlt` basics
* [dlt rest_api](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api) to learn how our `rest_api` source works

> This generator does not support OpenAPI 2.x FKA Swagger. If you need to use an older document, try upgrading it to
version 3 first with one of many available converters.


## Prior work
This project started as a fork of [openapi-python-client](https://github.com/openapi-generators/openapi-python-client). Pretty much all parts are heavily changed or completely replaced, but some lines of code still exist and we like to acknowledge the many good ideas we got from the original project :)


## Support
If you need support for this tool, [join our slack community](https://dlthub.com/community) and ask for help on the technical help channel. We're usually around to help you out or discuss features :)


## Features
The dlt-init-openapi generates code from an OpenAPI spec that you can use to extract data from a `rest_api` into any [`destination`](https://dlthub.com/docs/dlt-ecosystem/destinations/) (e.g. Postgres, BigQuery, Redshift...) `dlt` supports.

Features include

* **[Pagination](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api#pagination) discovery** for each endpoint
* **Primary key discovery** for each entity
* **Endpoint relationship mapping** into `dlt` [`transformers`](https://dlthub.com/docs/general-usage/resource#process-resources-with-dlttransformer) (e.g. /users/ -> /user/{id})
* **Payload JSON path [data selector](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api#data-selection) discovery** for results nested in the returned json
* **[Authentication](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api#authentication)** discovery for an API

## Setup

You will need Python 3.9 or higher installed, as well as pip.

```console
# 1. install this tool locally
$ pip install dlt-init-openapi

# 2. Show the version of the installed package to verify it worked
$ dlt-init-openapi --version
```

## Basic Usage

Let's create an example pipeline from the [PokeAPI spec](https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml). You can point to any other OpenAPI Spec instead if you like.

```console
# 1.a. Run the generator with an url:
$ dlt-init-openapi pokemon --url https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml

# 1.b. If you have a local file, you can use the --path flag:
$ dlt-init-openapi pokemon --path ./my_specs/pokeapi.yml

# 2. You can now pick the endpoints you need from the popup

# 3. After selecting your pokemon endpoints and hitting Enter, your pipeline will be rendered

# 4. If you have any kind of authentication on your pipeline (this example has not), open the `.dlt/secrets.toml` and provide the credentials. You can find further settings in the `.dlt/config.toml`.

# 5. Go to the created pipeline folder and run your pipeline
$ cd pokemon-pipeline
$ PROGRESS=enlighten python pipeline.py # we use enlighten for a nice progress bar :)

# 6. Print the pipeline info to console to see what got loaded
$ dlt pipeline pokemon_pipeline info

# 7. You can now also install streamlit to see a preview of the data
$ pip install pandas streamlit
$ dlt pipeline pokemon_pipeline show

# 8. You can go to our docs at https://dlthub.com/docs to learn how modify the generated pipeline to load to many destinations, place schema contracts on your pipeline and many other things.
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
$ dlt-init-openapi [OPTIONS] <source_name> [ARGS]
# example:
$ dlt-init-openapi pokemon --path ./path/to/my_spec.yml
```

**Options**:

- `--version`: Print the version and exit
- `--help`: Show this message and exit.

**Commands**:

- `init`: Generate a new `dlt` `rest_api` `source`

### `dlt-init-openapi`

Generate a new `dlt` `rest_api` `source`

**Usage**:

```console
$ dlt-init-openapi pokemon --path ./path/to/my_spec.yml
```

**Options**:

- `--url URL`: A url to read the OpenAPI JSON or YAML file from
- `--path PATH`: A path to read the OpenAPI JSON or YAML file from locally
- `--output-path PATH`: A path to render the output to
- `--config PATH`: Path to the config file to use (see below)
- `--no-interactive`: Skip endpoint selection and render all paths of the OpenAPI spec.
- `--loglevel`: Set logging level for stdout output, defaults to 20 (INFO).
- `--help`: Show this message and exit.

## Config options
You can pass a path to a config file with the `--config PATH` argument. To see available config values, go to https://github.com/dlt-hub/dlt-init-openapi/blob/devel/dlt_init_openapi/config.py and read the information below each field on the `Config` class.

The config file can be supplied as json or yaml dictionary. For example to change the package name, you can create a yaml file:

```yaml
# config.yml
package_name: "other_package_name"
```

And use it with the config argument:

```console
$ dlt-init-openapi pokemon --url ... --config config.yml
```

## Telemetry
We track your usage of this tool similar to how we track other commands in the dlt core library. Read more about this and how to disable it here: https://dlthub.com/docs/reference/telemetry.

## Implementation notes
* OAuth Authentication currently is not natively supported, you can supply your own
* Per endpoint authentication currently is not supported by the generator, only the first globally set securityScheme will be applied. You can add your own per endpoint if you need to.
