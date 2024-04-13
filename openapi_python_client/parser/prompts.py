from dataclasses import dataclass
from typing import Any

from openapi_python_client.parser.endpoints import Endpoint


@dataclass
class PropInfo:
    json_path: str
    is_optional: bool
    types: list[str]
    type_format: str | None
    description: str | None
    examples: list[Any]
    maximum: float | None
    default: Any | None

    def __str__(self) -> str:
        ret = ""
        ret += f"json_path: {self.json_path}\n"
        ret += f"is_optional: {self.is_optional}\n"
        ret += f"types: {', '.join(self.types)}\n"
        if self.type_format:
            ret += f"type_format: {self.type_format}\n"
        if self.default:
            ret += f"default: {self.default}\n"
        if self.maximum:
            ret += f"maximum: {self.maximum}\n"
        if self.description:
            ret += f"description: {self.description.strip()}\n"
        if self.examples:
            examples = ", ".join(str(e) for e in self.examples)
            ret += f"examples: {examples}\n"
        return ret


@dataclass
class ResponseInfo:
    status_code: str
    description: str | None
    schema_description: str | None
    properties: list[PropInfo]

    def __str__(self) -> str:
        ret = ""
        ret += f"status_code: {self.status_code}\n"
        if self.description:
            ret += f"description: {self.description.strip()}\n"
        if self.schema_description:
            ret += f"schema_description: {self.schema_description.strip()}\n"
        if self.properties:
            ret += "\nProperties:\n\n"
            for prop in self.properties:
                ret += str(prop) + "\n"
        return ret


@dataclass
class ParamInfo:
    name: str
    required: bool
    types: list[str]
    type_format: str | None
    description: str | None
    examples: list[Any]
    maximum: float | None
    default: Any | None
    location: str

    def __str__(self) -> str:
        ret = ""
        ret += f"name: {self.name}\n"
        ret += f"required: {self.required}\n"
        ret += f"location: {self.location}\n"
        ret += f"types: {', '.join(self.types)}\n"
        if self.type_format:
            ret += f"type_format: {self.type_format}\n"
        if self.default:
            ret += f"default: {self.default}\n"
        if self.maximum:
            ret += f"maximum: {self.maximum}\n"
        if self.description:
            ret += f"description: {self.description.strip()}\n"
        if self.examples:
            examples = ", ".join(str(e) for e in self.examples)
            ret += f"examples: {examples}\n"
        return ret


@dataclass
class EndpointInfo:
    path: str
    method: str
    description: str | None
    response: ResponseInfo
    parameters: list[ParamInfo]

    def __str__(self) -> str:
        ret = "endpoint: "
        ret += f"{self.method} {self.path}\n"
        if self.description:
            ret += f"description: {self.description.strip()}\n"
        if self.parameters:
            ret += "\nParameters:\n\n"
            for param in self.parameters:
                ret += str(param) + "\n"
        ret += "\nResponse:\n\n"
        ret += str(self.response)
        return ret


def create_endpoint_info(endpoint: Endpoint) -> EndpointInfo:
    """Collect a full presentation of params and response properties in the endpoint.
    params and properties include their names, descriptions, and types.
    """
    response_schema = endpoint.data_response.content_schema
    params = endpoint.parameters

    prop_infos: list[PropInfo] = []

    for path, schema in response_schema.crawled_properties.items():
        is_optional = response_schema.crawled_properties.is_optional(path)
        info = PropInfo(
            json_path=".".join(path),
            is_optional=is_optional,
            types=schema.types,  # type: ignore[arg-type]
            type_format=schema.type_format,
            description=schema.description,
            examples=schema.examples,
            maximum=schema.maximum,
            default=schema.default,
        )
        prop_infos.append(info)

    resp_info = ResponseInfo(
        status_code=endpoint.data_response.status_code,
        description=endpoint.data_response.description,
        schema_description=response_schema.description,
        properties=prop_infos,
    )

    param_infos = []
    for param in endpoint.parameters.values():
        param_info = ParamInfo(
            name=param.name,
            required=param.required,
            types=param.schema.types,  # type: ignore[arg-type]
            type_format=param.schema.type_format,
            description=param.schema.description,
            examples=param.schema.examples,
            maximum=param.schema.maximum,
            default=param.schema.default,
            location=param.location,
        )
        param_infos.append(param_info)

    return EndpointInfo(
        path=endpoint.path,
        method=endpoint.method,
        description=endpoint.description,
        response=resp_info,
        parameters=param_infos,
    )
