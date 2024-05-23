"""
Default open source detector
"""

import json
from typing import Dict, List, Optional, Tuple, Union, cast

from dlt_init_openapi.config import Config
from dlt_init_openapi.detector.base_detector import GLOBAL_WARNING_KEY, BaseDetector
from dlt_init_openapi.detector.default import utils
from dlt_init_openapi.detector.default.primary_key import detect_primary_key_by_name
from dlt_init_openapi.parser.endpoints import Endpoint, EndpointCollection, Response, TransformerSetting
from dlt_init_openapi.parser.models import DataPropertyPath
from dlt_init_openapi.parser.openapi_parser import OpenapiParser
from dlt_init_openapi.parser.pagination import Pagination
from dlt_init_openapi.parser.parameters import Parameter
from dlt_init_openapi.utils.misc import snake_case
from dlt_init_openapi.utils.paths import (
    get_non_var_path_parts,
    get_path_parts,
    get_path_var_names,
    path_looks_like_list,
    table_names_from_paths,
)

from .const import (
    DEFAULT_MAXIMUM_PAGINATOR_OFFSET,
    RE_CURSOR_PARAM,
    RE_CURSOR_PROP,
    RE_LIMIT_PARAM,
    RE_MATCH_ALL,
    RE_NEXT_PROPERTY,
    RE_OFFSET_PARAM,
    RE_PAGE_PARAM,
    RE_TOTAL_PAGE_PROPERTY,
    RE_TOTAL_PROPERTY,
    RE_UNIQUE_KEY,
)
from .utils import to_int
from .warnings import (
    BaseDetectionWarning,
    DataResponseNoBodyWarning,
    DataResponseUndetectedWarning,
    PossiblePaginatorWarning,
    PrimaryKeyNotFoundWarning,
    UnresolvedPathParametersWarning,
    UnsupportedSecuritySchemeWarning,
)

Tree = Dict[str, Union["str", "Tree"]]


class DefaultDetector(BaseDetector):

    warnings: Dict[str, List[BaseDetectionWarning]] = {}

    def __init__(self, config: Config) -> None:
        self.config = config

    def run(self, open_api: OpenapiParser) -> None:
        """Run the detector"""
        self.warnings = {}

        # detect security stuff
        self.detect_security_schemes(open_api)

        # discover stuff from responses
        self.detect_paginators_and_responses(open_api.endpoints)
        self.detect_global_pagination(open_api)

        # discover parent child relationship
        self.detect_parent_child_relationships(open_api.endpoints)

        # detect the mapping for mapping parent result values onto child path
        self.detect_transformer_settings(open_api.endpoints)

        # finally detect resource names
        self.detect_resource_names(open_api.endpoints)

        # and sort resources by table name
        open_api.endpoints.endpoints.sort(key=lambda e: e.detected_table_name)

        # add some warnings
        for e in open_api.endpoints.endpoints:
            if params := e.unresolvable_path_param_names:
                self._add_warning(UnresolvedPathParametersWarning(params), e)

    def detect_security_schemes(self, open_api: OpenapiParser) -> None:

        # detect scheme settings
        # TODO: make this a bit nicer
        for name, scheme in open_api.security_schemes.items():

            if scheme.type == "apiKey":
                scheme.detected_secret_names = ["api_key"]
                scheme.detected_auth_vars = f"""
            "type": "api_key",
            "api_key": api_key,
            "name": "{scheme.name}",
            "location": "{scheme.location}"
"""
            elif scheme.type == "http" and scheme.scheme == "basic":
                scheme.detected_secret_names = ["username", "password"]
                scheme.detected_auth_vars = """
            "type": "http_basic",
            "username": username,
            "password": password,
"""
            elif scheme.type == "http" and scheme.scheme == "bearer":
                scheme.detected_secret_names = ["token"]
                scheme.detected_auth_vars = """
            "type": "bearer",
            "token": token,
"""

        # find default scheme
        if open_api.global_security_name:
            global_scheme = None
            for name, scheme in open_api.security_schemes.items():
                if name == open_api.global_security_name:
                    global_scheme = scheme
                    break

            if global_scheme and global_scheme.supported:
                open_api.detected_global_security_scheme = global_scheme
            elif global_scheme and not global_scheme.supported:
                self._add_warning(UnsupportedSecuritySchemeWarning(global_scheme.type))

        # set first auth as global scheme
        if open_api.security_schemes and not open_api.detected_global_security_scheme:
            global_scheme = list(open_api.security_schemes.values())[0]
            if global_scheme.supported:
                open_api.detected_global_security_scheme = global_scheme

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
                parts = get_non_var_path_parts(endpoint.path)
                if len(parts):
                    name = utils.inf.singularize(parts[-1])
            endpoint.detected_resource_name = snake_case(name)
            endpoint.detected_table_name = snake_case(name)

        if resource_names_are_disctinct() and not self.config.name_resources_by_operation:
            return

        # now we try to build resource names from the path
        path_table_names = table_names_from_paths([e.path for e in endpoints.endpoints])
        for e in endpoints.endpoints:
            e.detected_resource_name = snake_case(path_table_names[e.path])
            if not e.detected_table_name:
                e.detected_table_name = snake_case(path_table_names[e.path])
        if resource_names_are_disctinct() and not self.config.name_resources_by_operation:
            return

        # last resort, we use the operation id, this should not happen really though
        for endpoint in endpoints.endpoints:
            endpoint.detected_resource_name = snake_case(endpoint.operation_id)

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
            endpoint.detected_data_response = self.detect_main_response(endpoint)

            # then detect pagination
            endpoint.detected_pagination = self.detect_pagination(endpoint)

            # with this info we can more safely detect the response payload
            if endpoint.detected_data_response:
                expect_list = (endpoint.detected_pagination is not None) or path_looks_like_list(endpoint.path)
                endpoint.detected_data_response.detected_payload = self.detect_response_payload(
                    endpoint.detected_data_response, expect_list=expect_list
                )
                self.detect_primary_key(endpoint, endpoint.detected_data_response, endpoint.path)

    def detect_global_pagination(self, open_api: OpenapiParser) -> None:
        """go through all detected paginators and see which one we can set as global"""
        paginator_by_key: Dict[str, Pagination] = {}
        paginator_count: Dict[str, int] = {}

        # count how many every paginator appears
        for endpoint in open_api.endpoints.endpoints:
            if not endpoint.detected_pagination:
                continue
            params = endpoint.detected_pagination.paginator_config
            key = json.dumps(params, sort_keys=True)
            paginator_by_key[key] = endpoint.detected_pagination
            paginator_count.setdefault(key, 0)
            paginator_count[key] += 1

        # no paginators found
        if len(paginator_by_key) == 0:
            return

        # sort dict by value descending, so most used paginator is at the top
        sorted_paginator_count = sorted(paginator_count.items(), key=lambda item: item[1] * -1)

        # we only set a global paginator, if we found one paginator, or if the top paginator has
        # a higher count than the second most used one
        if not (len(paginator_by_key) == 1 or sorted_paginator_count[0][1] > sorted_paginator_count[1][1]):
            return

        global_paginator = paginator_by_key[sorted_paginator_count[0][0]]

        # set global paginator on base object but also set on all endpoints
        open_api.detected_global_pagination = global_paginator
        for e in open_api.endpoints.endpoints:
            e.detected_global_pagination = global_paginator

    def detect_primary_key(self, e: Endpoint, response: Response, path: str) -> None:
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

        if not response.detected_primary_key:
            self._add_warning(PrimaryKeyNotFoundWarning(), e)

    def detect_main_response(self, endpoint: Endpoint) -> Optional[Response]:
        """Get main response and pagination for endpoint"""

        # find main response in list of responses
        main_response: Response = None
        for response in endpoint.responses:
            if response.status_code in ["200", "default"]:
                main_response = response
                break  # this will always be the right one
            if response.status_code.startswith("2") and not main_response:
                main_response = response

        if not main_response:
            self._add_warning(DataResponseUndetectedWarning(), endpoint)

        if main_response and not main_response.schema:
            self._add_warning(DataResponseNoBodyWarning(), endpoint)

        return main_response

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

        response_schema = endpoint.detected_data_response.schema if endpoint.detected_data_response else None

        page_params: List["Parameter"] = []
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
            if RE_PAGE_PARAM.match(param_name):
                page_params.append(param)

        #
        # Detect cursor
        #
        cursor_props: List[Tuple["Parameter", DataPropertyPath]] = []
        if response_schema:
            for cursor_param in cursor_params:
                # Try to response property to feed into the cursor param
                if prop := cursor_param.find_input_property(response_schema, fallback=None):
                    cursor_props.append((cursor_param, prop))

        # if we could not find matching prop in response, we can try to find the
        # matching prop in the response with a regex
        if response_schema and len(cursor_params) == 1 and not cursor_props:
            if prop := response_schema.nested_properties.find_property(RE_CURSOR_PROP):
                cursor_props.append((cursor_params[0], prop))

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
        if response_schema:
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
            limit_initial = to_int(limit_param.maximum) if limit_param.maximum else to_int(limit_param.default)
        total_prop = (
            response_schema.nested_properties.find_property(
                RE_TOTAL_PROPERTY, require_type="integer", allow_unknown_types=True
            )
            if response_schema
            else None
        )
        if offset_param and limit_param:

            pagination_config: Dict[str, Union[str, int]] = {
                "type": "offset",
                "limit": limit_initial or 20,
                "offset_param": offset_param.name,
                "limit_param": limit_param.name,
            }
            if total_prop:
                pagination_config["total_path"] = total_prop.json_path
            else:
                pagination_config["total_path"] = ""
                pagination_config["maximum_offset"] = DEFAULT_MAXIMUM_PAGINATOR_OFFSET

            return Pagination(
                paginator_config=pagination_config,
                pagination_params=[offset_param, limit_param],
            )

        #
        # detect page number paginator
        #
        if page_params:
            total_prop = None
            page_param = page_params[0]
            pagination_config = {
                "type": "page_number",
                "page_param": page_param.name,
            }
            total_prop = (
                response_schema.nested_properties.find_property(RE_TOTAL_PAGE_PROPERTY, require_type="integer")
                if response_schema
                else None
            )
            if total_prop:
                pagination_config["total_path"] = total_prop.json_path
            else:
                pagination_config["total_path"] = ""
                pagination_config["maximum_page"] = DEFAULT_MAXIMUM_PAGINATOR_OFFSET

            return Pagination(
                paginator_config=pagination_config,
                pagination_params=[page_param],
            )

        #
        # Detect json_links
        #
        if response_schema:
            next_prop = response_schema.nested_properties.find_property(RE_NEXT_PROPERTY, require_type="string")
            if next_prop:
                return Pagination(
                    paginator_config={"type": "json_response", "next_url_path": next_prop.json_path},
                    pagination_params=[offset_param, limit_param],
                )

        #
        # Nothing found :(
        #
        pagination_params = [*cursor_params, *offset_params, *limit_params, *page_params]
        if pagination_params:
            self._add_warning(PossiblePaginatorWarning([p.name for p in pagination_params]), endpoint)

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

    def get_warnings(self) -> Dict[str, List[BaseDetectionWarning]]:
        return self.warnings

    def _add_warning(self, warning: BaseDetectionWarning, e: Optional[Endpoint] = None) -> None:
        key = e.id if e else GLOBAL_WARNING_KEY
        warning_list = self.warnings.setdefault(key, [])
        warning_list.append(warning)
