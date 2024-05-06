"""
Default open source detector
"""
from typing import Dict, List, Optional, Tuple, Union

import openapi_schema_pydantic as osp

from openapi_python_client.detectors.base_detector import BaseDetector
from openapi_python_client.parser.endpoints import Response
from openapi_python_client.parser.models import DataPropertyPath, SchemaWrapper
from openapi_python_client.parser.pagination import Pagination
from openapi_python_client.parser.parameters import Parameter
from openapi_python_client.parser.paths import get_path_parts, is_var_part

from .const import RE_CURSOR_PARAM, RE_LIMIT_PARAM, RE_MATCH_ALL, RE_NEXT_PROPERTY, RE_OFFSET_PARAM, RE_TOTAL_PROPERTY


class DefaultDetector(BaseDetector):
    def detect_response_and_pagination(
        self, path: str, operation: osp.Operation, parameters: Dict[str, Parameter]
    ) -> Tuple[Optional[Pagination], Optional[Response]]:
        """Get main response and pagination from osp.operation"""

        # find main response in list of responses
        main_ref: Union[osp.Reference, osp.Response]
        for status_code, response_ref in operation.responses.items() or []:
            if status_code in ["200", "default"]:
                main_ref = response_ref
                break
            if str(status_code).startswith("2") and not main_ref:
                main_ref = response_ref

        # nothing found, return None
        if not main_ref:
            return None, None

        # find json content schema
        response_schema = self.context.response_from_reference(main_ref)
        content_schema: Optional[SchemaWrapper] = None
        for content_type, media_type in (response_schema.content or {}).items():
            if content_type.endswith("json") and media_type.media_type_schema:
                content_schema = SchemaWrapper.from_reference(media_type.media_type_schema, self.context)

        # build basic response, detect payload path later
        response = Response(response_schema=response_schema, content_schema=content_schema)

        # detect pagination
        pagination = self._detect_pagination(content_schema, parameters)

        # detect response payload path, we can give a hint wether we expect a list or not
        path_suggests_list = not is_var_part(get_path_parts(path)[-1])
        expect_list = (pagination is not None) or path_suggests_list
        response.payload = self.detect_payload(content_schema=content_schema, expect_list=expect_list)

        return pagination, response

    def detect_authentication(self) -> None:
        ...

    def detect_primary_key(self) -> None:
        ...

    def detect_parent_endpoint(self) -> None:
        ...

    def detect_transformer_mapping(self) -> None:
        ...

    def detect_payload(self, content_schema: SchemaWrapper, expect_list: bool) -> Optional[DataPropertyPath]:
        """Detect payload path in given schema"""
        payload: Optional[DataPropertyPath] = None

        # try to discover payload path and schema
        if content_schema:
            payload_path: List[str] = []

            if expect_list:
                if content_schema.is_list:
                    payload = DataPropertyPath(tuple(payload_path), content_schema)
                else:
                    payload = content_schema.crawled_properties.find_property(
                        RE_MATCH_ALL, "array", allow_unknown_types=False
                    )

            # either no list expected or no list found..
            if not payload:
                while len(content_schema.properties) == 1 and content_schema.properties[0].is_object:
                    # Schema contains only a single object property. The payload is inside
                    prop = content_schema.properties[0]
                    payload_path.append(prop.name)
                    content_schema = prop.schema
                payload = DataPropertyPath(tuple(payload_path), content_schema)

        return payload

    def _detect_pagination(
        self, content_schema: SchemaWrapper, parameters: Dict[str, Parameter]
    ) -> Optional[Pagination]:
        """Detect pagination from discovered main response and params of an endpoint"""

        if not content_schema:
            return None

        offset_params: List["Parameter"] = []
        cursor_params: List["Parameter"] = []
        limit_params: List["Parameter"] = []

        # Find params matching regexes
        for param_name, param in parameters.items():
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
            if prop := cursor_param.find_input_property(content_schema, fallback=None):
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
            prop = offset_param.find_input_property(content_schema, fallback=None)
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
        total_prop = content_schema.crawled_properties.find_property(RE_TOTAL_PROPERTY, require_type="integer")

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
        next_prop = content_schema.crawled_properties.find_property(RE_NEXT_PROPERTY, require_type="string")
        if next_prop:
            return Pagination(
                paginator_config={"type": "json_links", "next_url_path": next_prop.json_path},
                pagination_params=[offset_param, limit_param],
            )

        #
        # Nothing found :(
        #
        return None
