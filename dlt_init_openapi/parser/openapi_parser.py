import json
import sys
from typing import Any, Dict

import openapi_schema_pydantic as osp
import yaml
from loguru import logger
from yaml import BaseLoader

from dlt_init_openapi.exceptions import DltOpenAPIException
from dlt_init_openapi.parser.config import Config
from dlt_init_openapi.parser.context import OpenapiContext
from dlt_init_openapi.parser.endpoints import EndpointCollection
from dlt_init_openapi.parser.info import OpenApiInfo
from dlt_init_openapi.parser.pagination import Pagination
from dlt_init_openapi.parser.security import SecurityScheme


class OpenapiParser:
    info: OpenApiInfo
    context: OpenapiContext = None
    endpoints: EndpointCollection = None
    security_schemes: Dict[str, SecurityScheme] = {}

    global_security_name: str = None

    detected_global_security_scheme: SecurityScheme = None
    detected_global_pagination: Pagination = None

    def __init__(self, config: Config) -> None:
        self.config = config

    def parse(self, data: bytes) -> None:

        self.spec_raw = self._load_yaml_or_json(data)
        self.security_schemes = {}

        logger.info("Validating spec structure")
        try:
            spec = osp.OpenAPI.parse_obj(self.spec_raw)
        except Exception as e:
            raise DltOpenAPIException("Could not Validate spec:\n" + str(e)) from e
        logger.success("Spec validation successful")

        logger.info("Extracting openapi metadata")
        self.context = OpenapiContext(self.config, spec, self.spec_raw)
        self.info = OpenApiInfo.from_context(self.context)
        logger.success("Completed extracting openapi metadata and credentials.")

        logger.info("Extracting security schemes")
        if spec.security:
            self.global_security_name = list(spec.security[0].keys())[0]
        if self.context.spec.components and self.context.spec.components.securitySchemes:
            for name, scheme in self.context.spec.components.securitySchemes.items():
                self.security_schemes[name] = SecurityScheme(
                    name=scheme.name,  # type: ignore
                    type=scheme.type,  # type: ignore
                    scheme=scheme.scheme,  # type: ignore
                    location=scheme.security_scheme_in,  # type: ignore
                )
        logger.success("Completed extracting security schemes.")

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
