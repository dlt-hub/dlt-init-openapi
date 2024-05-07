"""
Default open source detector
"""
from typing import Dict, List, Optional, Tuple, Union, cast

import openapi_schema_pydantic as osp

from openapi_python_client.detector.base_detector import BaseDetector
from openapi_python_client.parser.endpoints import Endpoint, EndpointCollection, Response, TransformerSetting
from openapi_python_client.parser.models import DataPropertyPath, SchemaWrapper
from openapi_python_client.parser.openapi_parser import OpenapiContext, OpenapiParser
from openapi_python_client.parser.pagination import Pagination
from openapi_python_client.parser.parameters import Parameter
from openapi_python_client.utils.paths import get_path_parts, is_var_part

from .const import (
    RE_CURSOR_PARAM,
    RE_LIMIT_PARAM,
    RE_MATCH_ALL,
    RE_NEXT_PROPERTY,
    RE_OFFSET_PARAM,
    RE_TOTAL_PROPERTY,
    RE_UNIQUE_KEY,
)

Tree = Dict[str, Union["Endpoint", "Tree"]]


class DefaultDetector(BaseDetector):
    context: OpenapiContext

    def run(self, open_api: OpenapiParser) -> None:
        """Run the detector"""
        self.context = open_api.context

        # discover stuff from responses
        self.detect_paginators_and_responses(open_api.endpoints)

        # discover parent child relationship
        self.detect_parent_child_relationships(open_api.endpoints)

        self.detect_transformer_settings(open_api.endpoints)

    def detect_transformer_settings(self, endpoints: EndpointCollection) -> None:
        for endpoint in endpoints.endpoints:
            if not endpoint.parent or not endpoint.path_parameters or not endpoint.parent.payload:
                continue

            # TODO: figure out which one actually is the last path param
            param = list(endpoint.path_parameters.values())[-1]
            prop = param.find_input_property(endpoint.parent.payload.schema, fallback="id")

            if not prop:
                continue

            endpoint.detected_transformer_settings = TransformerSetting(
                parent_endpoint=endpoint.parent,
                parent_property=prop,
                path_parameter=param,
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
                path_suggests_list = not is_var_part(get_path_parts(endpoint.path)[-1])
                expect_list = (endpoint.detected_pagination is not None) or path_suggests_list
                endpoint.detected_response.detected_payload = self.detect_response_payload(
                    endpoint.detected_response, expect_list=expect_list
                )
                self.detect_primary_key(endpoint.detected_response)

    def detect_primary_key(self, response: Response) -> None:
        """detect the primary key from the payload
        TODO: we need way more primary key detection based on schema name etc."""
        if not response.detected_payload:
            return

        description_paths = []
        uuid_paths = []

        for prop in response.detected_payload.schema.all_properties:
            if prop.schema.types and (not set(prop.schema.types) & {"string", "integer"}):
                continue
            if prop.name.lower() == "id":
                response.detected_primary_key = prop.name
                return
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
        main_ref: Union[osp.Reference, osp.Response]
        for status_code, response_ref in endpoint.osp_operation.responses.items() or []:
            if status_code in ["200", "default"]:
                main_ref = response_ref
                break
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
        content_schema = response.schema

        # try to discover payload path and schema
        if content_schema:
            if expect_list:
                if content_schema.is_list:
                    payload = DataPropertyPath((), content_schema)
                else:
                    payload = content_schema.nested_properties.find_property(
                        RE_MATCH_ALL, "array", allow_unknown_types=False
                    )

            # either no list expected or no list found..
            if not payload:
                payload_path: List[str] = []
                while len(content_schema.properties) == 1 and content_schema.properties[0].is_object:
                    # Schema contains only a single object property. The payload may be inside.
                    prop = content_schema.properties[0]
                    payload_path.append(prop.name)
                    content_schema = prop.schema
                payload = DataPropertyPath(tuple(payload_path), content_schema)

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
        """detect parent child relationships based on path
        TODO: also discover /pokemons -> /pokemon/{id}
        """
        ENDPOINT_MARKER = "<endpoint>"

        # build endpoint tree
        tree: Tree = {}
        for endpoint in endpoints.endpoints:
            current_node = tree
            for part in endpoint.path_parts:
                if part not in current_node:
                    current_node[part] = {}
                current_node = current_node[part]  # type: ignore
            current_node[ENDPOINT_MARKER] = endpoint

        def find_nearest_list_parent(path: str) -> Optional[Endpoint]:
            parts = get_path_parts(path)
            while parts:
                current_node = tree
                parts.pop()
                for part in parts:
                    current_node = current_node[part]  # type: ignore[assignment]
                if parent_endpoint := current_node.get(ENDPOINT_MARKER):
                    if cast(Endpoint, parent_endpoint).is_list:
                        return cast(Endpoint, parent_endpoint)
            return None

        # link endpoints
        for endpoint in endpoints.endpoints:
            endpoint.detected_parent = find_nearest_list_parent(endpoint.path)
            if endpoint.detected_parent:
                endpoint.detected_parent.detected_children.append(endpoint)

    def detect_primary_keys(self, endpoints: EndpointCollection) -> None:
        pass
