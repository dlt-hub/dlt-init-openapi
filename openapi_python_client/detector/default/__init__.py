"""
Default open source detector
"""
from typing import Dict, List, Optional, Tuple, Union, cast

import openapi_schema_pydantic as osp

from openapi_python_client.detector.base_detector import BaseDetector
from openapi_python_client.detector.default import utils
from openapi_python_client.detector.default.primary_key import detect_primary_key_by_name
from openapi_python_client.parser.endpoints import Endpoint, EndpointCollection, Response, TransformerSetting
from openapi_python_client.parser.models import DataPropertyPath, SchemaWrapper
from openapi_python_client.parser.openapi_parser import OpenapiContext, OpenapiParser
from openapi_python_client.parser.pagination import Pagination
from openapi_python_client.parser.parameters import Parameter
from openapi_python_client.utils.paths import (
    get_path_parts,
    get_path_var_names,
    path_looks_like_list,
    table_names_from_paths,
)

from .const import (
    RE_CURSOR_PARAM,
    RE_LIMIT_PARAM,
    RE_MATCH_ALL,
    RE_NEXT_PROPERTY,
    RE_OFFSET_PARAM,
    RE_TOTAL_PROPERTY,
    RE_UNIQUE_KEY,
)

Tree = Dict[str, Union["str", "Tree"]]


class DefaultDetector(BaseDetector):
    context: OpenapiContext

    def __init__(self, force_operation_naming: bool = True) -> None:
        # forces naming to fallback to operation naming for testing
        self.force_operation_naming = force_operation_naming

    def run(self, open_api: OpenapiParser) -> None:
        """Run the detector"""
        self.context = open_api.context

        # discover stuff from responses
        self.detect_paginators_and_responses(open_api.endpoints)

        # discover parent child relationship
        self.detect_parent_child_relationships(open_api.endpoints)

        # detect the mapping for mapping parent result values onto child path
        self.detect_transformer_settings(open_api.endpoints)

        # finally detect resource names
        self.detect_resource_names(open_api.endpoints)

        # and sort resources by table name
        open_api.endpoints.endpoints.sort(key=lambda e: e.detected_table_name)

    def detect_resource_names(self, endpoints: EndpointCollection) -> None:
        """iterate all endpoints and find a strategy to select the right resource name"""

        def resource_names_are_disctinct() -> bool:
            """checks wether detected resource names are unique across all endpoints"""
            return len(endpoints.endpoints) == len({e.detected_resource_name for e in endpoints.endpoints})

        # best strategy is to use the entity name as resource name
        for endpoint in endpoints.endpoints:
            # try to use the name of the payload
            name = endpoint.payload.name if endpoint.payload else None
            # try to use the singularized last path element
            if not name:
                parts = utils.singularized_path_parts(endpoint.path)
                if len(parts):
                    name = parts[-1]
            endpoint.detected_resource_name = name
            endpoint.detected_table_name = name

        if resource_names_are_disctinct() and not self.force_operation_naming:
            return

        # now we try to build resource names from the path
        path_table_names = table_names_from_paths([e.path for e in endpoints.endpoints])
        for e in endpoints.endpoints:
            e.detected_resource_name = path_table_names[e.path]
            if not e.detected_table_name:
                e.detected_table_name = path_table_names[e.path]
        if resource_names_are_disctinct() and not self.force_operation_naming:
            return

        # last resort, we use the operation id, this should not happen really though
        for endpoint in endpoints.endpoints:
            endpoint.detected_resource_name = endpoint.operation_id

    def detect_transformer_settings(self, endpoints: EndpointCollection) -> None:
        for endpoint in endpoints.endpoints:
            if not endpoint.parent or not endpoint.parent.payload:
                continue
            ppayload = endpoint.parent.payload

            # Find the actual last param name in the path
            if not (path_params := get_path_var_names(endpoint.path)):
                continue
            param_name = path_params[-1]

            # try to match the path var to a property on the parent payload
            input_prop = None
            for prop in ppayload.schema.all_properties:
                if prop.name.lower() == param_name.lower():
                    input_prop = prop

            # fall back to primary key detected on the parent payload
            if not input_prop and endpoint.parent.primary_key:
                input_prop = ppayload.schema.all_properties_map[endpoint.parent.primary_key]

            # could not detect :(
            if not input_prop:
                continue

            endpoint.detected_transformer_settings = TransformerSetting(
                parent_property=DataPropertyPath((input_prop.name,), input_prop.schema),
                path_parameter_name=param_name,
            )

    def detect_paginators_and_responses(self, endpoints: EndpointCollection) -> None:
        # iterate over endpoints and detect response and pagination settings
        # order is important here, as some detections need the result of other
        # detections
        for endpoint in endpoints.endpoints:
            # first detect response
            endpoint.detected_response = self.detect_response_and_pagination(endpoint)

            # then detect pagination
            endpoint.detected_pagination = self.detect_pagination(endpoint)

            # with this info we can more safely detect the response payload
            if endpoint.detected_response:
                expect_list = (endpoint.detected_pagination is not None) or path_looks_like_list(endpoint.path)
                endpoint.detected_response.detected_payload = self.detect_response_payload(
                    endpoint.detected_response, expect_list=expect_list
                )
                self.detect_primary_key(endpoint.detected_response, endpoint.path)

    def detect_primary_key(self, response: Response, path: str) -> None:
        """detect the primary key from the payload"""
        if not response.detected_payload:
            return
        schema = response.detected_payload.schema

        # first, try to detect primary key by name, all props that are string, int or untyped are candidates
        primary_key_candidates = [
            prop.name
            for prop in schema.all_properties
            if (not prop.schema.types or set(prop.schema.types) & {"string", "integer"})
        ]
        response.detected_primary_key = detect_primary_key_by_name(primary_key_candidates, schema.name, path)
        if response.detected_primary_key:
            return

        # now try to do additional heuristics based on descriptions and prop type
        description_paths = []
        uuid_paths = []

        for prop in schema.all_properties:
            if prop.schema.types and (not set(prop.schema.types) & {"string", "integer"}):
                continue
            elif prop.schema.description and RE_UNIQUE_KEY.search(prop.schema.description):
                description_paths.append(prop.name)
            elif prop.schema.type_format == "uuid":
                uuid_paths.append(prop.name)

        if description_paths:
            response.detected_primary_key = description_paths[0]
        elif uuid_paths:
            response.detected_primary_key = uuid_paths[0]

    def detect_response_and_pagination(self, endpoint: Endpoint) -> Optional[Response]:
        """Get main response and pagination for endpoint"""

        # find main response in list of responses
        main_ref: Union[osp.Reference, osp.Response] = None
        for status_code, response_ref in endpoint.osp_operation.responses.items() or []:
            if status_code in ["200", "default"]:
                main_ref = response_ref
                break  # this will always be the right one
            if str(status_code).startswith("2") and not main_ref:
                main_ref = response_ref

        # nothing found, return None
        if not main_ref:
            return None

        # find json content schema
        response_schema = self.context.response_from_reference(main_ref)
        content_schema: Optional[SchemaWrapper] = None
        for content_type, media_type in (response_schema.content or {}).items():
            if content_type.endswith("json") and media_type.media_type_schema:
                content_schema = SchemaWrapper.from_reference(media_type.media_type_schema, self.context)
                break

        # build basic response, detect payload path later
        return Response(osp_response=response_schema, schema=content_schema)

    def detect_response_payload(self, response: Response, expect_list: bool) -> Optional[DataPropertyPath]:
        """Detect payload path in given schema"""
        payload: Optional[DataPropertyPath] = None

        # try to discover payload path and schema
        if response.schema:
            if expect_list:
                if response.schema.is_list:
                    payload = DataPropertyPath((), response.schema)
                else:
                    payload = response.schema.nested_properties.find_property(
                        RE_MATCH_ALL, "array", allow_unknown_types=False
                    )

            # either no list expected or no list found..
            if not payload:
                payload_path: List[str] = []
                while len(response.schema.properties) == 1 and response.schema.properties[0].is_object:
                    # Schema contains only a single object property. The payload may be inside.
                    prop = response.schema.properties[0]
                    payload_path.append(prop.name)
                    response.schema = prop.schema
                payload = DataPropertyPath(tuple(payload_path), response.schema)

        return payload

    def detect_pagination(self, endpoint: Endpoint) -> Optional[Pagination]:
        """Detect pagination from discovered main response and params of an endpoint"""

        response_schema = endpoint.detected_response.schema if endpoint.detected_response else None
        if not response_schema:
            return None

        offset_params: List["Parameter"] = []
        cursor_params: List["Parameter"] = []
        limit_params: List["Parameter"] = []

        # Find params matching regexes
        for param_name, param in endpoint.parameters.items():
            if RE_OFFSET_PARAM.match(param_name):
                offset_params.append(param)
            if RE_LIMIT_PARAM.match(param_name):
                limit_params.append(param)
            if RE_CURSOR_PARAM.match(param_name):
                cursor_params.append(param)

        #
        # Detect cursor
        #
        cursor_props: List[Tuple["Parameter", DataPropertyPath]] = []
        for cursor_param in cursor_params:
            # Try to response property to feed into the cursor param
            if prop := cursor_param.find_input_property(response_schema, fallback=None):
                cursor_props.append((cursor_param, prop))

        # Prefer the least nested cursor prop
        if cursor_props:
            cursor_props.sort(key=lambda x: len(x[1].path))
            cursor_param, cursor_prop = cursor_props[0]
            return Pagination(
                paginator_config={
                    "type": "cursor",
                    "cursor_path": cursor_prop.json_path,
                    "cursor_param": cursor_param.name,
                },
                pagination_params=[cursor_param],
            )

        #
        # Detect offset - limit
        #
        offset_props: List[Tuple["Parameter", DataPropertyPath]] = []
        offset_param: Optional["Parameter"] = None
        limit_param: Optional["Parameter"] = None
        limit_initial: Optional[int] = 20
        for offset_param in offset_params:
            # Try to response property to feed into the offset param
            prop = offset_param.find_input_property(response_schema, fallback=None)
            if prop:
                offset_props.append((offset_param, prop))
        # Prefer least nested offset prop
        if offset_props:
            offset_props.sort(key=lambda x: len(x[1].path))
            offset_param, offset_prop = offset_props[0]
        elif offset_params:  # No matching property found in response, fallback to use the first param detected
            offset_param = offset_params[0]
        for limit_param in limit_params:
            # When spec doesn't provide default/max limit, fallback to a conservative default
            # 20 should be safe for most APIs
            limit_initial = int(limit_param.maximum) if limit_param.maximum else (limit_param.default or 20)
        total_prop = response_schema.nested_properties.find_property(RE_TOTAL_PROPERTY, require_type="integer")

        if offset_param and limit_param and limit_initial and total_prop:
            return Pagination(
                paginator_config={
                    "type": "offset",
                    "initial_limit": limit_initial,
                    "offset_param": offset_param.name,
                    "limit_param": limit_param.name,
                    "total_path": total_prop.json_path,
                },
                pagination_params=[offset_param, limit_param],
            )

        #
        # Detect json_links
        #
        next_prop = response_schema.nested_properties.find_property(RE_NEXT_PROPERTY, require_type="string")
        if next_prop:
            return Pagination(
                paginator_config={"type": "json_links", "next_url_path": next_prop.json_path},
                pagination_params=[offset_param, limit_param],
            )

        #
        # Nothing found :(
        #
        return None

    def detect_parent_child_relationships(self, endpoints: EndpointCollection) -> None:
        """detect parent child relationships based on path"""
        ENDPOINT_MARKER = "<endpoint>"

        # save a map
        endpoint_map = endpoints.endpoints_by_path

        # determine if we can use normalized path parts, this means we singularize all
        # non param parts to be able to detect a relationship like /pokemons -> /pokemon/{id}
        singularized_paths = {"/".join(utils.singularized_path_parts(p)) for p in endpoint_map.keys()}
        can_singularize = len(singularized_paths) == len(endpoint_map.keys())

        # build endpoint tree
        tree: Tree = {}
        for endpoint in endpoints.endpoints:
            current_node = tree
            parts = utils.singularized_path_parts(endpoint.path) if can_singularize else get_path_parts(endpoint.path)
            for part in parts:
                if part not in current_node:
                    current_node[part] = {}
                current_node = current_node[part]  # type: ignore
            current_node[ENDPOINT_MARKER] = endpoint.path

        def find_nearest_list_parent(endpoint: Endpoint) -> Optional[Endpoint]:
            parts = utils.singularized_path_parts(endpoint.path) if can_singularize else get_path_parts(endpoint.path)
            while parts:
                current_node = tree
                parts.pop()
                for part in parts:
                    current_node = current_node[part]  # type: ignore[assignment]
                if parent_endpoint_path := cast(str, current_node.get(ENDPOINT_MARKER)):
                    found_endpoint = endpoint_map[parent_endpoint_path]
                    if found_endpoint.is_list:
                        return found_endpoint
            return None

        # link endpoints
        for endpoint in endpoints.endpoints:
            endpoint.detected_parent = find_nearest_list_parent(endpoint)
            if endpoint.detected_parent:
                endpoint.detected_parent.detected_children.append(endpoint)
