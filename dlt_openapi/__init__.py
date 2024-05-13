""" Generate modern Python clients from OpenAPI """

from enum import Enum
from importlib.metadata import version
from pathlib import Path
from typing import Optional, cast

from loguru import logger

from dlt_openapi.utils.misc import import_class_from_string

from .config import Config
from .detector.base_detector import BaseDetector
from .parser.openapi_parser import OpenapiParser
from .renderer.base_renderer import BaseRenderer

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
        self.openapi.parse()

    def detect(self) -> None:
        logger.info("Running heuristics on parsed output")
        self.detector.run(self.openapi)

    def render(self, dry: bool = False) -> None:
        logger.info("Rendering project")
        if self.config.endpoint_filter:
            filtered_endpoints = self.config.endpoint_filter(self.openapi.endpoints)
            self.openapi.endpoints.set_names_to_render(filtered_endpoints)
        self.renderer.run(self.openapi, dry=dry)


def _get_project_for_url_or_path(  # pylint: disable=too-many-arguments
    url: Optional[str],
    path: Optional[Path],
    config: Config = Config(),
) -> Project:
    renderer_cls = cast(BaseRenderer, import_class_from_string(config.renderer_class))
    detector_cls = cast(BaseDetector, import_class_from_string(config.detector_class))

    return Project(
        openapi=OpenapiParser(config, url or path),
        detector=detector_cls(config),  # type: ignore
        renderer=renderer_cls(config),  # type: ignore
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
