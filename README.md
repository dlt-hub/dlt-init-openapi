# dlt openapi source generator (dlt-init-openapi)
`dlt-init-openapi` generates [`dlt`](https://dlthub.com/docs) data pipelines from OpenAPI 3.x specs using the [`dlt` `rest_api` `verified source`](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api) to extract data from any rest API. If you do not know `dlt` or our `verified sources`, please read:

* [Getting started](https://dlthub.com/docs/getting-started) to learn the `dlt` basics
* [dlt rest_api](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api) to learn how our `rest_api` source works
* We also have a cool (google colab example)[https://colab.research.google.com/drive/1MRZvguOTZj1MlkEGzjiso8lQ_wr1MJRI?usp=sharing#scrollTo=LHGxzf1Ev_yr] that demonstrates this generator.


## Features
The dlt-init-openapi generates code from an OpenAPI spec that you can use to extract data from a `rest_api` into any [`destination`](https://dlthub.com/docs/dlt-ecosystem/destinations/) (e.g. Postgres, BigQuery, Redshift...) `dlt` supports. dlt-init-openapi additional executes a set of heuristics to discover information that is not explicetely defined in OpenAPI specs.

Features include

* **[Pagination](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api#pagination) discovery** for each endpoint
* **Primary key discovery** for each entity
* **Endpoint relationship mapping** into `dlt` [`transformers`](https://dlthub.com/docs/general-usage/resource#process-resources-with-dlttransformer) (e.g. /users/ -> /user/{id})
* **Payload JSON path [data selector](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api#data-selection) discovery** for results nested in the returned json
* **[Authentication](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api#authentication)** discovery for an API


## Support
If you need support for this tool or `dlt`, please [join our slack community](https://dlthub.com/community) and ask for help on the technical help channel. We're usually around to help you out or discuss features :)

## A quick example

You will need Python 3.9 or higher installed, as well as pip. You can run `pip install dlt-init-openapi` to install the current version.

We will create a simple example pipeline from a [PokeAPI spec](https://pokeapi.co/) in our repo. You can point to any other OpenAPI Spec instead if you like.

```console
# 1.a. Run the generator with an url:
$ dlt-init-openapi pokemon --url https://raw.githubusercontent.com/dlt-hub/dlt-init-openapi/devel/tests/cases/e2e_specs/pokeapi.yml --global-limit 2

# 1.b. If you have a local file, you can use the --path flag:
$ dlt-init-openapi pokemon --path ./my_specs/pokeapi.yml

# 2. You can now pick both of the endpoints from the popup

# 3. After selecting your pokemon endpoints and hitting Enter, your pipeline will be rendered.

# 4. If you have any kind of authentication on your pipeline (this example has not), open the `.dlt/secrets.toml` and provide the credentials. You can find further settings in the `.dlt/config.toml`.

# 5. Go to the created pipeline folder and run your pipeline
$ cd pokemon-pipeline
$ PROGRESS=enlighten python pipeline.py # we use enlighten for a nice progress bar :)

# 6. Print the pipeline info to console to see what got loaded
$ dlt pipeline pokemon_pipeline info

# 7. You can now also install streamlit to see a preview of the data, you should have loaded 40 pokemons and their details
$ pip install pandas streamlit
$ dlt pipeline pokemon_pipeline show

# 8. You can go to our docs at https://dlthub.com/docs to learn how modify the generated pipeline to load to many destinations, place schema contracts on your pipeline and many other things.

# NOTE: we used the `--global-limit 2` cli flag to limit the requests to the pokekom API for this example. This way the Pokemon collection endpoint only get's queried twice, resulting in 2 x 20 Pokemon details being rendered
```

## What will be created?

When you run the `init` command above, the following files will be generated:

```
pokemon_pipeline/
├── .dlt/
│   ├── config.toml     # dlt config, learn more at dlthub.com/docs
│   └── secrets.toml    # your secrets, only needed for APIs with auth
├── pokemon/
│   └── __init__.py     # your rest_api dictionary, learn more below
├── rest_api/
│   └── ...             # rest_api copied from our verified sources repo
├── .gitingore
├── pokemon_pipeline.py # your pipeline file that you can execute
├── README.md           # a list of your endpoints with some additional info
└── requirements.txt    # the pip requirements for your pipelin
```

> If you re-generate your pipeline, you will be prompted to continue if this folder exists. If you select yes, all generated files will be overwritten. All other files you may have created will remain in this folder.

## A closer look at pokemon/__init__.py

This file contains the configuration dictionary for the [dlt rest_api](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api) source which is the main result of running this generator. For our pokemon example we have used an OpenAPI 3 spec that works out of the box, the result of this dict depends on the quality of the spec you are using, wether the API you are querying actually adheres to this spec and wether our heuristics manage to find the right values. You can edit this file to adapt the behavior of the dlt rest_api accordingly, please read our [dlt rest_api](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api) docs to learn how to do this and play with our (google colab example)[https://colab.research.google.com/drive/1MRZvguOTZj1MlkEGzjiso8lQ_wr1MJRI?usp=sharing#scrollTo=LHGxzf1Ev_yr]

## CLI command

```console
$ dlt-init-openapi <source_name> [OPTIONS]
# example:
$ dlt-init-openapi pokemon --path ./path/to/my_spec.yml --no-interactive --output-path ./my_pipeline
```

**Options**:

_The only required options are either to supply a path or a url to a spec_

- `--url URL`: A url to read the OpenAPI JSON or YAML file from
- `--path PATH`: A path to read the OpenAPI JSON or YAML file from locally
- `--output-path PATH`: A path to render the output to
- `--config PATH`: Path to the config file to use (see below)
- `--no-interactive`: Skip endpoint selection and render all paths of the OpenAPI spec.
- `--log-level`: Set logging level for stdout output, defaults to 20 (INFO).
- `--global-limit`: Set a global limit on the generated source.
- `--update-rest-api-source`: Update the locally cached rest_api verified source.
- `--allow-openapi-2`: Allows to use OpenAPI v2. specs. Migration of the spec to 3.0 is recommended for better results though.
- `--version`: Show installed version of the generator and exit.
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

## Prior work
This project started as a fork of [openapi-python-client](https://github.com/openapi-generators/openapi-python-client). Pretty much all parts are heavily changed or completely replaced, but some lines of code still exist and we like to acknowledge the many good ideas we got from the original project :)

## Implementation notes
* OAuth Authentication currently is not natively supported, you can supply your own
* Per endpoint authentication currently is not supported by the generator, only the first globally set securityScheme will be applied. You can add your own per endpoint if you need to.
* Basic OpenAPI 2.0 support is implemented, we recommend updating your specs at https://editor.swagger.io before using `dlt-init-openapi`