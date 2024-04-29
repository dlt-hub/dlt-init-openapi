from __future__ import annotations

from typing import Optional, Literal, cast, Union, List, Dict, Any, Iterable, Tuple, Set

from dataclasses import dataclass, field
from itertools import groupby


import openapi_schema_pydantic as osp

from openapi_python_client.parser.context import OpenapiContext
from openapi_python_client.parser.paths import table_names_from_paths
from openapi_python_client.parser.models import SchemaWrapper, DataPropertyPath
from openapi_python_client.utils import PythonIdentifier
from openapi_python_client.parser.responses import process_responses
from openapi_python_client.parser.credentials import CredentialsProperty
from openapi_python_client.parser.pagination import Pagination
from openapi_python_client.parser.parameters import Parameter

TMethod = Literal["GET", "POST", "PUT", "PATCH"]
Tree = Dict[str, Union["Endpoint", "Tree"]]


@dataclass
class TransformerSetting:
    parent_endpoint: Endpoint
    # parent_property: DataPropertyPath
    # path_parameter: Parameter
    path_parameters: List[Parameter]
    parent_properties: List[DataPropertyPath]

    @property
    def path_params_mapping(self) -> Dict[str, str]:
        return {param.name: prop.json_path for param, prop in zip(self.path_parameters, self.parent_properties)}


@dataclass
class Response:
    status_code: str
    description: str
    raw_schema: osp.Response
    content_schema: Optional[SchemaWrapper]
    list_property: Optional[DataPropertyPath] = None
    payload: Optional[DataPropertyPath] = None
    initial_payload: Optional[DataPropertyPath] = None
    """Payload set initially before comparing other endpoints"""

    @property
    def has_content(self) -> bool:
        """Whether this is a no-content response"""
        return bool(self.content_schema)
        # return bool(self.content_schema and self.content_schema.has_properties)

    @property
    def list_properties(self) -> Dict[Tuple[str, ...], SchemaWrapper]:
        """Paths to list properties"""
        if not self.content_schema:
            return {}
        return self.content_schema.crawled_properties.list_properties

    @property
    def object_properties(self) -> Dict[Tuple[str, ...], SchemaWrapper]:
        """Paths to object properties"""
        if not self.content_schema:
            return {}
        return self.content_schema.crawled_properties.object_properties

    @classmethod
    def from_reference(
        cls, status_code: str, resp_ref: Union[osp.Reference, osp.Response], context: OpenapiContext
    ) -> "Response":
        if status_code == "default":
            status_code = "200"
        raw_schema = context.response_from_reference(resp_ref)
        description = resp_ref.description or raw_schema.description

        content_schema: Optional[SchemaWrapper] = None
        for content_type, media_type in (raw_schema.content or {}).items():
            # Look for json responses only
            if (content_type == "application/json" or content_type.endswith("+json")) and media_type.media_type_schema:
                content_schema = SchemaWrapper.from_reference(media_type.media_type_schema, context)

        payload_schema: Optional[SchemaWrapper] = content_schema
        payload: Optional[DataPropertyPath] = None
        if payload_schema:
            payload_path = []
            while len(payload_schema.properties) == 1 and payload_schema.properties[0].is_object:
                # Schema contains only a single object property. The payload is inside
                prop_obj = payload_schema.properties[0]
                payload_path.append(prop_obj.name)
                payload_schema = prop_obj.schema
            payload = DataPropertyPath(tuple(payload_path), payload_schema)

        return cls(
            status_code=status_code,
            description=description,
            raw_schema=raw_schema,
            content_schema=content_schema,
            payload=payload,
            initial_payload=payload,
        )


@dataclass()
class Endpoint:
    method: TMethod
    responses: Dict[str, Response]
    path: str
    parameters: Dict[str, Parameter]
    path_table_name: str
    """Table name inferred from path"""
    raw_schema: osp.Operation

    operation_id: str

    python_name: PythonIdentifier
    credentials: Optional[CredentialsProperty]

    _parent: Optional["Endpoint"] = None
    children: List["Endpoint"] = field(default_factory=list)

    summary: Optional[str] = None
    description: Optional[str] = None

    path_summary: Optional[str] = None
    """Summary applying to all methods of the path"""
    path_description: Optional[str] = None
    """Description applying to all methods of the path"""

    pagination: Optional[Pagination] = None

    rank: int = 0

    def get_imports(self) -> List[str]:
        """Get all import strings required to use this endpoint"""
        imports: List[str] = []
        if self.credentials:
            imports.extend(self.credentials.get_imports())
        for param in self.parameters.values():
            imports.extend(param.get_imports())
        return imports

    def to_docstring(self) -> str:
        lines = [self.path_summary, self.summary, self.path_description, self.description]
        return "\n".join(line for line in lines if line)

    @property
    def payload(self) -> Optional[DataPropertyPath]:
        if not self.data_response:
            return None
        return self.data_response.payload

    @property
    def is_list(self) -> bool:
        payload = self.payload
        return payload.is_list if payload else False

    @property
    def parent(self) -> Optional["Endpoint"]:
        return self._parent

    @parent.setter
    def parent(self, value: Optional["Endpoint"]) -> None:
        self._parent = value
        if value:
            value.children.append(self)

    @property
    def primary_key(self) -> Optional[str]:
        payload = self.payload
        return payload.schema.primary_key if payload else None

    @property
    def path_parameters(self) -> Dict[str, Parameter]:
        return {p.name: p for p in self.parameters.values() if p.location == "path"}

    @property
    def query_parameters(self) -> Dict[str, Parameter]:
        return {p.name: p for p in self.parameters.values() if p.location == "query"}

    @property
    def header_parameters(self) -> Dict[str, Parameter]:
        return {p.name: p for p in self.parameters.values() if p.location == "header"}

    @property
    def cookie_parameters(self) -> Dict[str, Parameter]:
        return {p.name: p for p in self.parameters.values() if p.location == "cookie"}

    @property
    def list_all_parameters(self) -> List[Parameter]:
        return list(self.parameters.values())

    def positional_arguments(self) -> List[Parameter]:
        include_path_params = not self.transformer
        ret = (p for p in self.parameters.values() if p.required and p.default is None)
        # exclude pagination params
        if self.pagination:
            ret = (p for p in ret if p.name not in self.pagination.param_names)
        if not include_path_params:
            ret = (p for p in ret if p.location != "path")
        return list(ret)

    def keyword_arguments(self) -> List[Parameter]:
        ret = (p for p in self.parameters.values() if not p.required)
        # exclude pagination params
        if self.pagination:
            ret = (p for p in ret if p.name not in self.pagination.param_names)
        return list(ret)

    def all_arguments(self) -> List[Parameter]:
        return self.positional_arguments() + self.keyword_arguments()

    @property
    def request_args_meta(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Mapping of how to translate python arguments to request parameters"""
        result: Dict[str, Any] = {}
        for param in self.parameters.values():
            items = result.setdefault(param.location, {})
            items[param.python_name] = {
                "name": param.name,
                "types": param.types,
                "explode": param.explode,
                "style": param.style,
            }
        return result

    @property
    def request_args_meta_str(self) -> str:
        return repr(self.request_args_meta)

    @property
    def data_response(self) -> Optional[Response]:
        if not self.responses:
            return None
        keys = list(self.responses.keys())
        if len(keys) == 1:
            return self.responses[keys[0]]
        success_codes = [k for k in keys if k.startswith("20")]
        if success_codes:
            return self.responses[success_codes[0]]
        return self.responses[keys[0]]

    @property
    def has_content(self) -> bool:
        resp = self.data_response
        return bool(resp) and resp.has_content

    @property
    def table_name(self) -> str:
        name: Optional[str] = None
        if self.payload:
            name = self.payload.name
        if name:
            return name
        return self.path_table_name

    # @property
    # def list_property(self) -> Optional[DataPropertyPath]:
    #     if not self.data_response:
    #         return None
    #     return self.data_response.list_property

    @property
    def data_json_path(self) -> str:
        payload = self.payload
        return (payload.json_path if payload else "") or "$"

    # @property
    # def is_transformer(self) -> bool:
    #     return not not self.path_parameters

    @property
    def transformer(self) -> Optional[TransformerSetting]:
        # TODO: compute once when generating endpoints
        if not self.parent:
            return None
        # if not self.parent.is_list:
        #     return None
        path_parameters = self.path_parameters
        if not path_parameters:
            return None
        # # Are we nested more than 1 level?
        # # Must ensure all path params are resolved in parent transformers
        # if len(self.path_parameters) > 1:
        #     for i in range(len(self.path_parameters) - 1):
        #         parent = self.parent
        #         if not parent.is_transformer:
        #             return None

        # Must resolve all path parameters from the parent response
        # TODO: Consider multiple levels of transformers.
        # This would need to forward resolved ancestor params through meta arg
        parent_payload = self.parent.payload
        assert parent_payload
        resolved_props = []
        for param in path_parameters.values():
            prop = param.find_input_property(parent_payload.schema, fallback="id")
            if not prop:
                return None
            resolved_props.append(prop)

        return TransformerSetting(
            parent_endpoint=self.parent,
            parent_properties=resolved_props,
            path_parameters=list(path_parameters.values()),
        )

        # path_param = list(self.path_parameters.values())[-1]
        # payload = self.parent.payload
        # assert payload
        # list_object = payload.prop
        # # transformer_arg = list_object.crawled_properties.find_property_by_name(path_param.name, fallback="id")
        # transformer_arg = path_param.find_input_property(list_object, fallback="id")
        # if not transformer_arg:
        #     return None
        # return TransformerSetting(
        #     parent_endpoint=self.parent, parent_property=transformer_arg, path_parameter=path_param
        # )

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

        parsed_responses = (
            Response.from_reference(status_code, response_ref, context)
            for status_code, response_ref in operation.responses.items()
        )
        responses = {}
        for parsed_response in parsed_responses:
            if parsed_response.status_code in responses:
                continue
            responses[parsed_response.status_code] = parsed_response

        operation_id = operation.operationId or f"{method}_{path}"

        credentials = CredentialsProperty.from_requirements(operation.security, context) if operation.security else None

        endpoint = cls(
            method=method,
            path=path,
            raw_schema=operation,
            responses=responses,
            parameters=all_params,
            path_table_name=path_table_name,
            operation_id=operation_id,
            python_name=PythonIdentifier(operation_id),
            summary=operation.summary,
            description=operation.description,
            path_summary=path_summary,
            path_description=path_description,
            credentials=credentials,
        )
        endpoint.pagination = Pagination.from_endpoint(endpoint)
        return endpoint


@dataclass
class EndpointCollection:
    endpoints: List[Endpoint]
    endpoint_tree: Tree
    names_to_render: Optional[Set[str]] = None

    @property
    def all_endpoints_to_render(self) -> List[Endpoint]:
        # return [e for e in self.endpoints if e.has_content]
        # Sum of endpoint ranks by table name
        to_render = sorted(
            [
                e
                for e in self.endpoints
                if (not self.names_to_render or e.python_name in self.names_to_render) and e.has_content
            ],
            key=lambda e: e.table_name,
        )
        groups = groupby(to_render, key=lambda e: e.table_name)
        groups = [(name, list(group)) for name, group in groups]  # type: ignore[assignment]
        groups = sorted(groups, key=lambda g: max(e.rank for e in g[1]), reverse=True)  # type: ignore[assignment]
        return [e for _, group in groups for e in group]

    @property
    def endpoints_by_id(self) -> Dict[str, Endpoint]:
        """Endpoints by operation ID"""
        return {ep.operation_id: ep for ep in self.endpoints}

    @property
    def endpoints_by_path(self) -> Dict[str, Endpoint]:
        """Endpoints by path"""
        return {ep.path: ep for ep in self.endpoints}

    @property
    def root_endpoints(self) -> List[Endpoint]:
        return [e for e in self.all_endpoints_to_render if e.is_list and not e.path_parameters]

    @property
    def transformer_endpoints(self) -> List[Endpoint]:
        return [e for e in self.all_endpoints_to_render if e.transformer]

    def set_names_to_render(self, names: Set[str]) -> None:
        self.names_to_render = names

    @classmethod
    def from_context(cls, context: OpenapiContext) -> "EndpointCollection":
        endpoints: list[Endpoint] = []
        all_paths = list(context.spec.paths)
        path_table_names = table_names_from_paths(all_paths)
        for path, path_item in context.spec.paths.items():
            path_level_params = [Parameter.from_reference(param, context) for param in path_item.parameters or []]
            for op_name in context.config.include_methods:
                operation = getattr(path_item, op_name)
                if not operation:
                    continue
                endpoints.append(
                    Endpoint.from_operation(
                        cast(TMethod, op_name.upper()),
                        path,
                        operation,
                        path_table_names[path],
                        path_level_params,
                        path_item.summary,
                        path_item.description,
                        context,
                    )
                )
        endpoint_tree = cls.build_endpoint_tree(endpoints)
        result = cls(endpoints=endpoints, endpoint_tree=endpoint_tree)
        process_responses(result)
        for endpoint in result.endpoints:
            endpoint.parent = result.find_nearest_list_parent(endpoint.path)
        for endpoint in result.root_endpoints:
            Pagination.from_endpoint(endpoint)
        return result

    def find_immediate_parent(self, path: str) -> Optional[Endpoint]:
        """Find the parent of the given endpoint.

        Example:
            `find_immediate_parent('/api/v2/ability/{id}') -> Endpoint<'/api/v2/ability'>`
        """
        parts = path.strip("/").split("/")
        while parts:
            current_node = self.endpoint_tree
            parts.pop()
            for part in parts:
                current_node = current_node[part]  # type: ignore
            if "<endpoint>" in current_node:
                return current_node["<endpoint>"]  # type: ignore
        return None

    def find_nearest_list_parent(self, path: str) -> Optional[Endpoint]:
        parts = path.strip("/").split("/")
        while parts:
            current_node = self.endpoint_tree
            parts.pop()
            for part in parts:
                current_node = current_node[part]  # type: ignore[assignment]
            if parent_endpoint := current_node.get("<endpoint>"):
                if cast(Endpoint, parent_endpoint).is_list:
                    return cast(Endpoint, parent_endpoint)
        return None

    @staticmethod
    def build_endpoint_tree(endpoints: Iterable[Endpoint]) -> Tree:
        tree: Tree = {}
        for endpoint in endpoints:
            path = endpoint.path
            parts = path.strip("/").split("/")
            current_node = tree
            for part in parts:
                if part not in current_node:
                    current_node[part] = {}
                current_node = current_node[part]  # type: ignore
            current_node["<endpoint>"] = endpoint
        return tree

    def _endpoint_tree_to_str(self) -> str:
        # Pretty print presentation of the tree
        def _tree_to_str(node: Union["Endpoint", "Tree"], indent: int = 0) -> str:
            if isinstance(node, dict):
                return "\n".join(
                    f"{'  ' * indent}{key}\n{_tree_to_str(value, indent + 1)}" for key, value in node.items()
                )
            return f"{'  ' * indent}{node.path} -> {node.operation_id}"

        return _tree_to_str(self.endpoint_tree)
