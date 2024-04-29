# `openapi-python-client`

Generate a Python client from an OpenAPI JSON document

**Usage**:

```console
$ dlt-init [OPTIONS] COMMAND [ARGS]...
# e.g.: dlt-init init pokemon --url https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml

```

**Options**:

- `--version`: Print the version and exit [default: False]
- `--install-completion`: Install completion for the current shell.
- `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
- `--help`: Show this message and exit.

**Commands**:

- `generate`: Generate a new OpenAPI Client library
- `update`: Update an existing OpenAPI Client library

## `openapi-python-client generate`

Generate a new OpenAPI Client library

**Usage**:

```console
$ openapi-python-client generate [OPTIONS]
```

**Options**:

- `--url TEXT`: A URL to read the JSON from
- `--path PATH`: A path to the JSON file
- `--custom-template-path DIRECTORY`: A path to a directory containing custom template(s)
- `--meta [none|poetry|setup]`: The type of metadata you want to generate. [default: poetry]
- `--file-encoding TEXT`: Encoding used when writing generated [default: utf-8]
- `--config PATH`: Path to the config file to use
- `--help`: Show this message and exit.

## `openapi-python-client update`

Update an existing OpenAPI Client library

> **Note:** The `update` command performs the same operations as `generate` except it does not overwrite specific metadata for the generated client such as the `README.md`, `.gitignore`, and `pyproject.toml`.

**Usage**:

```console
$ openapi-python-client update [OPTIONS]
```

**Options**:

- `--url TEXT`: A URL to read the JSON from
- `--path PATH`: A path to the JSON file
- `--custom-template-path DIRECTORY`: A path to a directory containing custom template(s)
- `--meta [none|poetry|setup]`: The type of metadata you want to generate. [default: poetry]
- `--file-encoding TEXT`: Encoding used when writing generated [default: utf-8]
- `--config PATH`: Path to the config file to use
- `--help`: Show this message and exit.
