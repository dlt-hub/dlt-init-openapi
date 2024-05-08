""" Generate modern Python clients from OpenAPI """

import logging
from enum import Enum
from importlib.metadata import version
from pathlib import Path
from typing import Optional

from .config import Config
from .detector.base_detector import BaseDetector
from .parser.openapi_parser import OpenapiParser
from .renderer.base_renderer import BaseRenderer

log = logging.getLogger(__name__)

__version__ = version(__package__)


class MetaType(str, Enum):
    """The types of metadata supported for project generation."""

    NONE = "none"
    POETRY = "poetry"
    SETUP = "setup"


class Project:  # pylint: disable=too-many-instance-attributes
    """Represents a Python project (the top level file-tree) to generate"""

    def __init__(
        self,
        *,
        openapi: OpenapiParser,
        detector: BaseDetector,
        renderer: BaseRenderer,
        config: Config,
    ) -> None:
        self.openapi = openapi
        self.detector = detector
        self.renderer = renderer
        self.config = config

    def parse(self) -> None:
        log.info("Parse spec")
        self.openapi.parse()
        log.info("Parsing completed")

    def detect(self) -> None:
        log.info("Detecting parsed output")
        self.detector.run(self.openapi)
        log.info("Detecting completed")

    def render(self, dry: bool = False) -> None:
        log.info("Rendering project")
        if self.config.endpoint_filter:
            filtered_endpoints = self.config.endpoint_filter(self.openapi.endpoints)
            self.openapi.endpoints.set_names_to_render(filtered_endpoints)
        self.renderer.run(self.openapi, dry=dry)
        log.info("Rendering complete")


def _get_project_for_url_or_path(  # pylint: disable=too-many-arguments
    url: Optional[str],
    path: Optional[Path],
    config: Config = Config(),
) -> Project:
    log.info("Running detector")
    from openapi_python_client.detector.default import DefaultDetector
    from openapi_python_client.renderer.default import DefaultRenderer

    return Project(
        openapi=OpenapiParser(config, url or path),
        detector=DefaultDetector(config),
        renderer=DefaultRenderer(config),
        config=config,
    )


def create_new_client(
    *,
    url: Optional[str] = None,
    path: Optional[Path] = None,
    config: Config = Config(),
) -> Project:
    """
    Generate the client library

    Returns:
        The project.
    """
    project = _get_project_for_url_or_path(
        url=url,
        path=path,
        config=config,
    )
    project.parse()
    project.detect()
    project.render()
    return project
