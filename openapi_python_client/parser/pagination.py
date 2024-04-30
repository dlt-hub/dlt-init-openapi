import re

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, List, Dict, Tuple, Any

from openapi_python_client.parser.models import DataPropertyPath

if TYPE_CHECKING:
    from openapi_python_client.parser.endpoints import Endpoint, Parameter

RE_OFFSET_PARAM = re.compile(r"(?i)(page|start|offset)")
RE_LIMIT_PARAM = re.compile(r"(?i)(limit|per_page|page_size|size)")
RE_TOTAL_PROPERTY = re.compile(r"(?i)(total|count)")
RE_CURSOR_PARAM = re.compile(r"(?i)(cursor|after|since)")


@dataclass
class Pagination:
    pagination_params: List["Parameter"] = field(default_factory=list)
    paginator_config: Dict[str, str] = None

    @property
    def param_names(self) -> List[str]:
        """All params used for pagination"""
        return [param.name for param in self.pagination_params]

    @classmethod
    def from_endpoint(cls, endpoint: "Endpoint") -> Optional["Pagination"]:
        resp = endpoint.data_response
        if not resp or not resp.content_schema:
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

        cursor_props: List[Tuple["Parameter", DataPropertyPath]] = []
        for cursor_param in cursor_params:
            # Try to response property to feed into the cursor param
            prop = cursor_param.find_input_property(resp.content_schema, fallback=None)
            if prop:
                cursor_props.append((cursor_param, prop))

        pagination_config: Optional[Dict[str, Any]] = None
        # Prefer the least nested cursor prop
        if cursor_props:
            cursor_props.sort(key=lambda x: len(x[1].path))
            cursor_param, cursor_prop = cursor_props[0]
            pagination_config = {
                "type": "cursor",
                "cursor_path": cursor_prop.json_path,
                "cursor_param": cursor_param.name,
            }
            return cls(
                paginator_config=pagination_config,
                pagination_params=[cursor_param],
            )

        offset_props: List[Tuple["Parameter", DataPropertyPath]] = []
        offset_param: Optional["Parameter"] = None
        limit_param: Optional["Parameter"] = None
        limit_initial: Optional[int] = 20
        for offset_param in offset_params:
            # Try to response property to feed into the offset param
            prop = offset_param.find_input_property(resp.content_schema, fallback=None)
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

        if offset_param and limit_param and limit_initial:
            pagination_config = {
                "type": "offset",
                "initial_limit": limit_initial,
                "offset_param": offset_param.name,
                "limit_param": limit_param.name,
            }
            return cls(
                paginator_config=pagination_config,
                pagination_params=[offset_param, limit_param],
            )

        # No pagination detected
        return None
