""" Generate modern Python clients from OpenAPI """

from enum import Enum
from importlib.metadata import version
from pathlib import Path
from typing import cast

import httpcore
import httpx
from loguru import logger

from dlt_init_openapi.utils.misc import import_class_from_string

from .config import Config
from .detector.base_detector import GLOBAL_WARNING_KEY, BaseDetector
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
        doc: bytes,
        openapi: OpenapiParser,
        detector: BaseDetector,
        renderer: BaseRenderer,
        config: Config,
    ) -> None:
        self.doc = doc
        self.openapi = openapi
        self.detector = detector
        self.renderer = renderer
        self.config = config

    def parse(self) -> None:
        self.openapi.parse(self.doc)

    def detect(self) -> None:
        logger.info("Running heuristics on parsed output")
        self.detector.run(self.openapi)
        logger.success("Heuristics completed")

    def render(self, dry: bool = False) -> None:
        logger.info("Rendering project")
        if self.config.endpoint_filter:
            filtered_endpoints = self.config.endpoint_filter(self.openapi.endpoints)
            if filtered_endpoints:
                self.openapi.endpoints.set_ids_to_render(filtered_endpoints)
            else:
                logger.warning("You have not selected any endpoints, all endpoints will be rendered.")
        self.renderer.run(self.openapi, dry=dry)
        logger.success(f"Rendered project to: {self.config.project_dir}")
        logger.info("You can now run your pipeline from this folder with 'python pipeline.py'.")

    def print_warnings(self) -> None:
        """print warnings to logger if any where encountered for endpoints that are being rendered"""
        warnings = self.detector.get_warnings()
        if not warnings:
            logger.info("No warnings generated during parsing and detection")
            return

        # print the global warnings
        if global_warnings := warnings.get(GLOBAL_WARNING_KEY):
            logger.warning("Global warnings:")
            for w in global_warnings:
                logger.warning(w.msg)

        # print warnings, but only for endpoints that where rendered
        for endpoint_id, endpoint_warnings in warnings.items():
            if endpoint_id in self.openapi.endpoints.endpoint_ids_to_render:
                e = self.openapi.endpoints.endpoints_by_id[endpoint_id]
                logger.warning(f"Warnings for endpoint {e.method} {e.path}:")
                for w in endpoint_warnings:
                    logger.warning(w.msg)


def _get_document(*, config: Config, timeout: int = 60) -> bytes:
    if config.spec_url is not None and config.spec_path is not None:
        raise ValueError("Provide URL or Path, not both.")
    if config.spec_url is not None:
        logger.info(f"Downloading spec from {config.spec_url}")
        try:
            response = httpx.get(config.spec_url, timeout=timeout)
            logger.success("Download complete")
            return response.content
        except (httpx.HTTPError, httpcore.NetworkError) as e:
            raise ValueError("Could not get OpenAPI document from provided URL") from e
    elif config.spec_path is not None:
        logger.info(f"Reading spec from {config.spec_path}")
        return Path(config.spec_path).read_bytes()
    else:
        raise ValueError("No URL or Path provided")


def _get_project_for_url_or_path(  # pylint: disable=too-many-arguments
    config: Config = None,
) -> Project:
    doc = _get_document(config=config)

    renderer_cls = cast(BaseRenderer, import_class_from_string(config.renderer_class))
    detector_cls = cast(BaseDetector, import_class_from_string(config.detector_class))

    return Project(
        doc=doc,
        openapi=OpenapiParser(config),
        detector=detector_cls(config),  # type: ignore
        renderer=renderer_cls(config),  # type: ignore
        config=config,
    )


def create_new_client(
    *,
    config: Config = None,
) -> Project:
    """
    Generate the client library

    Returns:
        The project.
    """
    project = _get_project_for_url_or_path(
        config=config,
    )
    project.parse()
    project.detect()
    project.render()
    project.print_warnings()
    return project
