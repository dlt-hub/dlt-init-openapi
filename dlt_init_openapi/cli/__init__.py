import pathlib
import sys
from typing import Any, Optional

import questionary
import typer
from dlt.cli import utils
from loguru import logger

from dlt_init_openapi.cli.cli_endpoint_selection import questionary_endpoint_selection
from dlt_init_openapi.config import Config
from dlt_init_openapi.exceptions import DltOpenAPITerminalException
from dlt_init_openapi.utils import update_rest_api

app = typer.Typer(add_completion=False)


def _print_version(value: bool) -> None:
    from dlt_init_openapi import __version__

    if value:
        typer.echo(f"dlt-init-openapi version: {__version__}")
        raise typer.Exit()


def _load_config(path: Optional[pathlib.Path], config: Any) -> Config:
    if not path:
        c = Config(**config)
    else:
        try:
            c = Config.load_from_path(path=path, **config)
        except Exception as err:
            raise typer.BadParameter("Unable to parse config") from err
    return c


# pylint: disable=too-many-arguments
@app.command()
def init(
    source: str = typer.Argument(None, help="A name of data source for which to generate a pipeline"),
    url: Optional[str] = typer.Option(None, help="A URL to read the JSON/YAML spec from"),
    path: Optional[pathlib.Path] = typer.Option(None, help="A path to the JSON/YAML spec file"),
    output_path: Optional[pathlib.Path] = typer.Option(None, help="A path to render the output to."),
    config_path: Optional[pathlib.Path] = typer.Option(None, "--config", help="Path to the config file to use"),
    interactive: bool = typer.Option(True, help="Wether to select needed endpoints interactively"),
    log_level: int = typer.Option(20, help="Set logging level for stdout output, defaults to 20 (INFO)"),
    global_limit: int = typer.Option(0, help="Set a global limit on the generated source"),
    allow_openapi_2: bool = typer.Option(
        False,
        "--allow-openapi-2",
        help="Allow to use OpenAPI v2. specs. Migration of the spec to 3.0 is recommended though.",
    ),
    update_rest_api_source: bool = typer.Option(False, help="Update the locally cached rest_api verified source."),
    version: bool = typer.Option(False, "--version", callback=_print_version, help="Print the version and exit"),
) -> None:
    """Generate a new dlt pipeline"""

    _init_command_wrapped(
        source=source,
        url=url,
        path=path,
        output_path=output_path,
        config_path=config_path,
        interactive=interactive,
        log_level=log_level,
        global_limit=global_limit,
        update_rest_api_source=update_rest_api_source,
        allow_openapi_2=allow_openapi_2,
    )


@utils.track_command("init-openapi", False, "source", "url", "path")
def _init_command_wrapped(
    source: str,
    url: Optional[str] = None,
    path: Optional[pathlib.Path] = None,
    output_path: Optional[pathlib.Path] = None,
    config_path: Optional[pathlib.Path] = None,
    interactive: bool = True,
    log_level: int = 20,
    global_limit: int = 0,
    update_rest_api_source: bool = False,
    allow_openapi_2: bool = False,
) -> None:

    from dlt_init_openapi import create_new_client

    # set up console logging
    logger.remove()
    logger.add(sys.stdout, level=log_level)
    logger.success("Starting dlt openapi generator")

    if not url and not path:
        typer.secho("You must either provide --url or --path", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    if url and path:
        typer.secho("Provide either --url or --path, not both", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    try:

        # sync rest api
        update_rest_api.update_rest_api(force=update_rest_api_source)

        config = _load_config(
            path=config_path,
            config={
                "project_name": source,
                "package_name": source,
                "output_path": output_path,
                "endpoint_filter": questionary_endpoint_selection if interactive else None,
                "global_limit": global_limit,
                "spec_url": url,
                "spec_path": path,
                "allow_openapi_2": allow_openapi_2,
            },
        )

        if config.project_dir.exists():
            if not interactive:
                logger.info("Non interactive mode selected, overwriting existing source.")
            elif not questionary.confirm(
                f"Directory {config.project_dir} exists, do you want to continue and update the generated files? "
                + "This will overwrite your changes in those files."
            ).ask():
                logger.warning("Exiting...")
                exit(0)

        create_new_client(
            config=config,
        )
        logger.success("Pipeline created. Learn more at https://dlthub.com/docs. See you next time :)")

    except DltOpenAPITerminalException as exc:
        logger.error("Encountered terminal exception:")
        logger.error(exc)
        logger.info("Exiting...")
