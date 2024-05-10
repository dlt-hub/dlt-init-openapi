import pathlib
from typing import Optional

import typer

from dlt_openapi.cli.cli_endpoint_selection import questionary_endpoint_selection
from dlt_openapi.config import Config

app = typer.Typer()


def _print_version(value: bool) -> None:
    from dlt_openapi import __version__

    if value:
        typer.echo(f"dlt-openapi version: {__version__}")
        raise typer.Exit()


def _load_config(path: Optional[pathlib.Path]) -> Config:
    if not path:
        return Config()
    try:
        return Config.load_from_path(path=path)
    except Exception as err:
        raise typer.BadParameter("Unable to parse config") from err


# noinspection PyUnusedLocal
# pylint: disable=unused-argument
@app.callback(name="dlt-openapi")
def cli(
    version: bool = typer.Option(False, "--version", callback=_print_version, help="Print the version and exit"),
) -> None:
    """Generate a Python client from an OpenAPI JSON document"""


CONFIG_OPTION = typer.Option(None, "--config", help="Path to the config file to use")


# pylint: disable=too-many-arguments
@app.command()
def init(
    source: str = typer.Argument(None, help="A name of data source for which to generate a pipeline"),
    url: Optional[str] = typer.Option(None, help="A URL to read the JSON from"),
    path: Optional[pathlib.Path] = typer.Option(None, help="A path to the JSON file"),
    config_path: Optional[pathlib.Path] = CONFIG_OPTION,
    interactive: bool = typer.Option(True, help="Wether to select needed endpoints interactively"),
) -> None:
    """Generate a new OpenAPI Client library"""
    from dlt_openapi import create_new_client

    if not url and not path:
        typer.secho("You must either provide --url or --path", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    if url and path:
        typer.secho("Provide either --url or --path, not both", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    config = _load_config(config_path)
    config.project_name = source
    config.package_name = source
    config.endpoint_filter = questionary_endpoint_selection if interactive else None
    create_new_client(
        url=url,
        path=path,
        config=config,
    )
