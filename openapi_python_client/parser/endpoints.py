from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Set, Union, cast

import openapi_schema_pydantic as osp

from openapi_python_client.parser.context import OpenapiContext
from openapi_python_client.parser.models import DataPropertyPath, SchemaWrapper
from openapi_python_client.parser.pagination import Pagination
from openapi_python_client.parser.parameters import Parameter
from openapi_python_client.parser.paths import get_path_parts, is_var_part, table_names_from_paths

TMethod = Literal["GET", "POST", "PUT", "PATCH"]


@dataclass
class TransformerSetting:
    parent_endpoint: Endpoint
    path_parameters: List[Parameter]
    parent_properties: List[DataPropertyPath]

    @property
    def path_params_mapping(self) -> Dict[str, str]:
        return {param.name: prop.json_path for param, prop in zip(self.path_parameters, self.parent_properties)}

    @property
    def path_params_mapping_first_item(self) -> Dict[str, str]:
        items = self.path_params_mapping
        if items:
            key = list(items.keys())[0]
            return {key: items[key]}
        return items


@dataclass
class Response:
    response_schema: osp.Response
    content_schema: Optional[SchemaWrapper]
    # detected values
    detected_payload: Optional[DataPropertyPath] = None
    detected_primary_key: Optional[str] = None


@dataclass()
class Endpoint:
    operation_schema: osp.Operation

    # basic parser results
    method: TMethod
    path: str
    parameters: Dict[str, Parameter]
    operation_id: str
    summary: Optional[str] = None
    description: Optional[str] = None
    path_summary: Optional[str] = None
    """Summary applying to all methods of the path"""
    path_description: Optional[str] = None
    """Description applying to all methods of the path"""

    # inferred values
    path_table_name: Optional[str] = None
    """Table name inferred from path"""

    # detected values
    detected_pagination: Optional[Pagination] = None
    detected_response: Optional[Response] = None
    detected_resource_name: Optional[str] = None  # TODO
    detected_parent: Optional["Endpoint"] = None
    detected_children: List["Endpoint"] = field(default_factory=list)

    @property
    def payload(self) -> Optional[DataPropertyPath]:
        if not self.detected_response:
            return None
        return self.detected_response.detected_payload

    @property
    def is_list(self) -> bool:
        """if we know the payload, we can discover from there, if not assume list if last path part is not arg"""
        return self.payload.is_list if self.payload else (not is_var_part(self.path_parts[-1]))

    @property
    def parent(self) -> Optional["Endpoint"]:
        return self.detected_parent

    @property
    def primary_key(self) -> Optional[str]:
        return self.detected_response.detected_primary_key if self.detected_response else None

    @property
    def path_parts(self) -> List[str]:
        return get_path_parts(self.path)

    @property
    def path_parameters(self) -> Dict[str, Parameter]:
        return {p.name: p for p in self.parameters.values() if p.location == "path"}

    @property
    def list_all_parameters(self) -> List[Parameter]:
        return list(self.parameters.values())

    def positional_arguments(self) -> List[Parameter]:
        include_path_params = not self.transformer
        ret = (p for p in self.parameters.values() if p.required and p.default is None)
        # exclude pagination params
        if self.detected_pagination:
            ret = (p for p in ret if p.name not in self.detected_pagination.param_names)
        if not include_path_params:
            ret = (p for p in ret if p.location != "path")
        return list(ret)

    def keyword_arguments(self) -> List[Parameter]:
        ret = (p for p in self.parameters.values() if not p.required)
        # exclude pagination params
        if self.detected_pagination:
            ret = (p for p in ret if p.name not in self.detected_pagination.param_names)
        return list(ret)

    @property
    def pagination_args(self) -> Optional[Dict[str, Union[str, int]]]:
        return self.detected_pagination.paginator_config if self.detected_pagination else None

    def all_arguments(self) -> List[Parameter]:
        return self.positional_arguments() + self.keyword_arguments()

    @property
    def table_name(self) -> str:
        return self.payload.name if (self.payload and self.payload.name) else self.path_table_name

    @property
    def data_json_path(self) -> str:
        return self.payload.json_path if self.payload else "$"

    @property
    def transformer(self) -> Optional[TransformerSetting]:
        # meet a couple of conditions to be a transformer
        if not self.parent or not self.path_parameters or not self.parent.payload:
            return None

        resolved_props = []
        for param in self.path_parameters.values():
            prop = param.find_input_property(self.parent.payload.schema, fallback="id")
            if not prop:
                return None
            resolved_props.append(prop)

        return TransformerSetting(
            parent_endpoint=self.parent,
            parent_properties=resolved_props,
            path_parameters=list(self.path_parameters.values()),
        )

    @classmethod
    def from_operation(
        cls,
        method: TMethod,
        path: str,
        operation: osp.Operation,
        path_table_name: str,
        path_level_parameters: List[Parameter],
        path_summary: Optional[str],
        path_description: Optional[str],
        context: OpenapiContext,
    ) -> "Endpoint":
        # Merge operation params with top level params from path definition
        all_params = {p.name: p for p in path_level_parameters}
        all_params.update(
            {p.name: p for p in (Parameter.from_reference(param, context) for param in operation.parameters or [])}
        )

        return cls(
            method=method,
            path=path,
            operation_schema=operation,
            parameters=all_params,
            path_table_name=path_table_name,
            operation_id=operation.operationId or f"{method}_{path}",
            summary=operation.summary,
            description=operation.description,
            path_summary=path_summary,
            path_description=path_description,
        )


@dataclass
class EndpointCollection:
    endpoints: List[Endpoint]
    names_to_render: Optional[Set[str]] = None

    @property
    def all_endpoints_to_render(self) -> List[Endpoint]:
        """get all endpoints we want to render
        TODO: render parent child relationships correctly
        """
        if not self.names_to_render:
            return self.endpoints
        return [e for e in self.endpoints if e.operation_id in self.names_to_render]

    @property
    def endpoints_by_path(self) -> Dict[str, Endpoint]:
        """Endpoints by path"""
        return {ep.path: ep for ep in self.endpoints}

    @property
    def root_endpoints(self) -> List[Endpoint]:
        """Endpoints we can run without path params"""
        return [e for e in self.all_endpoints_to_render if not e.path_parameters]

    @property
    def transformer_endpoints(self) -> List[Endpoint]:
        return [e for e in self.all_endpoints_to_render if e.transformer]

    def set_names_to_render(self, names: Set[str]) -> None:
        self.names_to_render = names

    @classmethod
    def from_context(cls, context: OpenapiContext) -> "EndpointCollection":
        endpoints: list[Endpoint] = []
        endpoint_paths = list(context.spec.paths)
        path_table_names = table_names_from_paths(endpoint_paths)
        for path, path_item in context.spec.paths.items():
            for op_name in context.config.include_methods:
                if not (operation := getattr(path_item, op_name)):
                    continue
                endpoints.append(
                    Endpoint.from_operation(
                        cast(TMethod, op_name.upper()),
                        path,
                        operation,
                        path_table_names[path],
                        [Parameter.from_reference(param, context) for param in path_item.parameters or []],
                        path_item.summary,
                        path_item.description,
                        context,
                    )
                )
        return cls(endpoints=endpoints)
