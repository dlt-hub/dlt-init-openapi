import json
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Union
from urllib.parse import urlparse

import httpcore
import httpx
import openapi_schema_pydantic as osp
import yaml
from loguru import logger
from yaml import BaseLoader

from dlt_openapi.parser.config import Config
from dlt_openapi.parser.context import OpenapiContext
from dlt_openapi.parser.credentials import CredentialsProperty
from dlt_openapi.parser.endpoints import EndpointCollection
from dlt_openapi.parser.info import OpenApiInfo


class OpenapiParser:
    spec_raw: Dict[str, Any]
    info: OpenApiInfo
    credentials: Optional[CredentialsProperty] = None
    context: OpenapiContext

    def __init__(self, config: Config, spec_file: Union[Path, str]) -> None:
        self.spec_file = spec_file
        # self.context = OpenapiContext(config=config)
        self.config = config

    def load_spec_raw(self) -> Dict[str, Any]:
        p = self.spec_file
        if isinstance(p, Path):
            return _get_document(path=p)
        parsed = urlparse(p)
        if parsed.scheme in ("http", "https"):
            return _get_document(url=p)
        return _get_document(path=Path(p))

    def _find_references(self, dictionary: Dict[str, Any]) -> Iterator[str]:
        """Iterate all schema URI references in the spec ($ref fields)"""
        if isinstance(dictionary, dict):
            if "$ref" in dictionary and isinstance(dictionary["$ref"], str):
                ref = dictionary["$ref"]
                if not ref.startswith("#/"):
                    logger.warning("$ref url %s is not supported", ref)
                else:
                    yield dictionary["$ref"]
            else:
                for key, value in dictionary.items():
                    yield from self._find_references(value)
        elif isinstance(dictionary, list):
            for item in dictionary:
                yield from self._find_references(item)

    def parse(self) -> None:
        self.spec_raw = self.load_spec_raw()

        logger.info("Validating spec structure")
        spec = osp.OpenAPI.parse_obj(self.spec_raw)

        logger.info("Extracting openapi metadata")
        self.context = OpenapiContext(self.config, spec, self.spec_raw)
        self.info = OpenApiInfo.from_context(self.context)

        logger.info("Parsing openapi endpoints")
        self.endpoints = EndpointCollection.from_context(self.context)

        logger.info("Parsing openapi credentials")
        self.credentials = CredentialsProperty.from_context(self.context)


def _load_yaml_or_json(data: bytes) -> Dict[str, Any]:
    logger.info("Trying to parse as JSON")
    try:
        return json.loads(data.decode())
    except ValueError:
        logger.info("No valid JSON found")
        pass

    logger.info("Trying to parse as YAML")
    return yaml.load(data, Loader=BaseLoader)


def _get_document(*, url: Optional[str] = None, path: Optional[Path] = None, timeout: int = 60) -> Dict[str, Any]:
    if url is not None and path is not None:
        raise ValueError("Provide URL or Path, not both.")
    if url is not None:
        logger.info(f"Downloading spec from {url}")
        try:
            response = httpx.get(url, timeout=timeout)
            logger.info("Download complete")
            return _load_yaml_or_json(response.content)
        except (httpx.HTTPError, httpcore.NetworkError) as e:
            raise ValueError("Could not get OpenAPI document from provided URL") from e
    elif path is not None:
        logger.info("Loading spec from %s", path)
        return _load_yaml_or_json(path.read_bytes())
    else:
        raise ValueError("No URL or Path provided")
