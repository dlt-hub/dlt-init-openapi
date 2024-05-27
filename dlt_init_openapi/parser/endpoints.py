from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Set, Union, cast

import openapi_schema_pydantic as osp
from loguru import logger

from dlt_init_openapi.parser.context import OpenapiContext
from dlt_init_openapi.parser.models import DataPropertyPath, SchemaWrapper
from dlt_init_openapi.parser.pagination import Pagination
from dlt_init_openapi.parser.parameters import Parameter
from dlt_init_openapi.utils.paths import get_path_var_names, path_looks_like_list

TMethod = Literal["GET", "POST", "PUT", "PATCH"]


@dataclass
class TransformerSetting:
    path_parameter_name: str
    parent_property: DataPropertyPath

    @property
    def path_params_mapping(self) -> Dict[str, str]:
        return {self.path_parameter_name: self.parent_property.json_path}


@dataclass
class Response:
    osp_response: osp.Response
    schema: Optional[SchemaWrapper]
    status_code: str
    description: str
    # detected values
    detected_payload: Optional[DataPropertyPath] = None
    detected_primary_key: Optional[str] = None


@dataclass()
class Endpoint:
    osp_operation: osp.Operation
    context: OpenapiContext

    # basic parser results
    method: TMethod
    path: str
    parameters: Dict[str, Parameter]
    responses: List[Response]
    operation_id: str
    summary: Optional[str] = None
    description: Optional[str] = None
    path_summary: Optional[str] = None
    """Summary applying to all methods of the path"""
    path_description: Optional[str] = None
    """Description applying to all methods of the path"""

    # detected values
    detected_pagination: Optional[Pagination] = None
    detected_global_pagination: Optional[Pagination] = None
    detected_data_response: Optional[Response] = None
    detected_resource_name: Optional[str] = None
    detected_table_name: Optional[str] = None
    detected_parent: Optional["Endpoint"] = None
    detected_children: List["Endpoint"] = field(default_factory=list)
    detected_transformer_settings: Optional[TransformerSetting] = None

    @property
    def id(self) -> str:
        """unique identifier"""
        return self.operation_id

    @property
    def payload(self) -> Optional[DataPropertyPath]:
        """gets payload dataproperty path if detected"""
        return self.detected_data_response.detected_payload if self.detected_data_response else None

    @property
    def is_list(self) -> bool:
        """if we know the payload, we can discover from there, if not assume list if last path part is not arg"""
        return self.payload.is_list if self.payload else path_looks_like_list(self.path)

    @property
    def parent(self) -> Optional["Endpoint"]:
        return self.detected_parent

    @property
    def primary_key(self) -> Optional[str]:
        return self.detected_data_response.detected_primary_key if self.detected_data_response else None

    @property
    def list_all_parameters(self) -> List[Parameter]:
        return list(self.parameters.values())

    @property
    def render_pagination_args(self) -> Optional[Dict[str, Union[str, int]]]:
        # if own paginator equals global paginator, do not render anything
        if self.detected_pagination == self.detected_global_pagination:
            return None
        return self.detected_pagination.paginator_config if self.detected_pagination else None

    @property
    def render_auto_paginator(self) -> bool:
        """if we could not figure out the paginator, set it to auto"""
        # we do not set auto if there is a global paginator, this is a bug in the underlying layer, we have to fix this
        # once rest_api is fixed
        if self.detected_global_pagination:
            return False
        return not (self.detected_pagination)

    @property
    def data_json_path(self) -> str:
        return self.payload.json_path if self.payload else None

    @property
    def transformer(self) -> Optional[TransformerSetting]:
        return self.detected_transformer_settings

    @property
    def unresolvable_path_param_names(self) -> List[str]:
        """returns a list of path param names with params that are resolvable via the parent excluded"""
        params = get_path_var_names(self.path)
        transformer_param = self.transformer.path_parameter_name if self.transformer else None
        return [p for p in params if p != transformer_param]

    @property
    def unresolvable_query_params(self) -> List[Parameter]:
        """returns a list of required query param names with params that are used by the paginator excluded"""
        paginator_params = self.detected_pagination.param_names if self.detected_pagination else []
        query_params: List[Parameter] = []
        for param in self.list_all_parameters:
            if param.name not in paginator_params and param.location == "query":
                query_params.append(param)
        return query_params

    @property
    def unresolvable_required_query_param_names(self) -> List[str]:
        """returns a list of required query param names with params that are used by the paginator excluded"""
        return [param.name for param in self.unresolvable_query_params if param.required]

    @property
    def unresolvable_unrequired_query_param_names(self) -> List[str]:
        return [param.name for param in self.unresolvable_query_params if not param.required]

    def default_for_param(self, location: Literal["path", "query"], param_name: str) -> str:
        """get's a default value for the given param, returns"""
        param: Parameter = None
        for key, p in self.parameters.items():
            if p.name == param_name and p.location == location:
                param = p
        if param and param.default:
            return param.default
        if not param or param.required or location == "path":
            return self.context.config.required_parameter_default_value
        return self.context.config.unrequired_parameter_default_value

    @property
    def render_description(self) -> Optional[str]:
        description = self.description or self.path_description
        if not description:
            return None
        return description.replace("\n", " ")

    @classmethod
    def from_operation(
        cls,
        method: TMethod,
        path: str,
        osp_operation: osp.Operation,
        path_level_parameters: List[Parameter],
        path_summary: Optional[str],
        path_description: Optional[str],
        context: OpenapiContext,
    ) -> "Endpoint":
        # Merge operation params with top level params from path definition
        all_params = {p.name: p for p in path_level_parameters}
        all_params.update(
            {p.name: p for p in (Parameter.from_reference(param, context) for param in osp_operation.parameters or [])}
        )

        # get all responses
        responses: List[Response] = []
        for status_code, response_ref in osp_operation.responses.items() or []:
            # find json content schema
            response_schema = context.response_from_reference(response_ref)
            content_schema: Optional[SchemaWrapper] = None
            for content_type, media_type in (response_schema.content or {}).items():
                if (content_type.endswith("json") or content_type == "*/*") and media_type.media_type_schema:
                    content_schema = SchemaWrapper.from_reference(media_type.media_type_schema, context)
                    break

            responses.append(
                Response(
                    osp_response=response_schema,
                    schema=content_schema,
                    status_code=status_code,
                    description=response_schema.description,
                )
            )

        return cls(
            method=method,
            path=path,
            osp_operation=osp_operation,
            responses=responses,
            parameters=all_params,
            operation_id=osp_operation.operationId or f"{method}_{path}",
            summary=osp_operation.summary,
            description=osp_operation.description,
            path_summary=path_summary,
            path_description=path_description,
            context=context,
        )


@dataclass
class EndpointCollection:
    endpoints: List[Endpoint]
    endpoint_ids_to_render: Set[str] = field(default_factory=set)
    endpoint_ids_to_deselect: Set[str] = field(default_factory=set)

    @property
    def all_endpoints_to_render(self) -> List[Endpoint]:
        """get all endpoints we want to render"""
        return [e for e in self.endpoints if e.id in self.endpoint_ids_to_render]

    @property
    def endpoints_by_path(self) -> Dict[str, Endpoint]:
        """Endpoints by path"""
        return {ep.path: ep for ep in self.endpoints}

    @property
    def endpoints_by_id(self) -> Dict[str, Endpoint]:
        """Endpoints by path"""
        return {ep.id: ep for ep in self.endpoints}

    def set_ids_to_render(self, ids: Set[str]) -> None:
        selected_ids = set()
        ids_to_render = set()

        # traverse ancestry chain and make sure parent endpoints are also marked for rendering
        # but deselected
        for endpoint_id in ids:
            ep = self.endpoints_by_id[endpoint_id]
            ids_to_render.add(ep.id)
            selected_ids.add(ep.id)
            while ep.transformer and ep.parent:
                ids_to_render.add(ep.parent.id)
                ep = ep.parent
        self.endpoint_ids_to_render = ids_to_render
        self.endpoint_ids_to_deselect = ids_to_render - selected_ids

    @classmethod
    def from_context(cls, context: OpenapiContext) -> "EndpointCollection":
        endpoints: list[Endpoint] = []
        for path, path_item in context.spec.paths.items():
            for op_name in context.config.include_methods:
                if not (operation := getattr(path_item, op_name)):
                    continue
                logger.info(f"Found endpoint {op_name.upper()} {path}")
                endpoints.append(
                    Endpoint.from_operation(
                        method=cast(TMethod, op_name.upper()),
                        path=path,
                        osp_operation=operation,
                        path_level_parameters=[
                            Parameter.from_reference(param, context) for param in path_item.parameters or []
                        ],
                        path_summary=path_item.summary,
                        path_description=path_item.description,
                        context=context,
                    )
                )
        return cls(endpoints=endpoints, endpoint_ids_to_render={e.id for e in endpoints})
