import json
import sys
from typing import Any, Dict, Optional

import openapi_schema_pydantic as osp
import yaml
from loguru import logger
from yaml import BaseLoader

from dlt_openapi.exceptions import DltOpenAPIException
from dlt_openapi.parser.config import Config
from dlt_openapi.parser.context import OpenapiContext
from dlt_openapi.parser.credentials import CredentialsProperty
from dlt_openapi.parser.endpoints import EndpointCollection
from dlt_openapi.parser.info import OpenApiInfo


class OpenapiParser:
    info: OpenApiInfo
    credentials: Optional[CredentialsProperty] = None

    context: OpenapiContext = None
    endpoints: EndpointCollection = None

    def __init__(self, config: Config) -> None:
        self.config = config

    def parse(self, data: bytes) -> None:
        self.spec_raw = self._load_yaml_or_json(data)

        logger.info("Validating spec structure")
        try:
            spec = osp.OpenAPI.parse_obj(self.spec_raw)
        except Exception as e:
            raise DltOpenAPIException("Could not Validate spec:\n" + str(e)) from e
        logger.success("Spec validation successful")

        logger.info("Extracting openapi metadata")
        self.context = OpenapiContext(self.config, spec, self.spec_raw)
        self.credentials = CredentialsProperty.from_context(self.context)
        self.info = OpenApiInfo.from_context(self.context)
        logger.success("Completed extracting openapi metadata and credentials.")

        logger.info("Parsing openapi endpoints")
        self.endpoints = EndpointCollection.from_context(self.context)
        logger.success(f"Completed parsing endpoints. {len(self.endpoints.endpoints)} endpoints found.")

    def _load_yaml_or_json(self, data: bytes) -> Dict[str, Any]:
        logger.info("Trying to parse spec as JSON")

        data_size = sys.getsizeof(data)
        if data_size > 1000000:
            mb = round(data_size / 1000000)
            logger.warning(f"Spec is around {mb} mb, so parsing might take a while.")
        try:
            result = json.loads(data.decode())
            logger.success("Parsed spec as JSON")
            return result
        except ValueError:
            logger.info("No valid JSON found")
            pass
        logger.info("Trying to parse spec as YAML")
        result = yaml.load(data, Loader=BaseLoader)
        logger.success("Parsed spec as YAML")
        return result
