from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Tuple

if TYPE_CHECKING:
    from openapi_python_client.parser.endpoints import EndpointCollection, Endpoint, Response

from openapi_python_client.parser.models import DataPropertyPath
from openapi_python_client.utils import count_by_length
from openapi_python_client.parser.paths import find_longest_common_prefix


def process_responses(endpoint_collection: "EndpointCollection") -> None:
    """Process all responses in schemas"""
    all_endpoints = endpoint_collection.all_endpoints_to_render
    table_ranks: Dict[str, int] = {}
    for endpoint in all_endpoints:
        _process_response_list(endpoint.data_response, endpoint, endpoint_collection)
        response = endpoint.data_response
        unique_models = set(t.name for t in response.content_schema.crawled_properties.object_properties.values())
        table_ranks[endpoint.table_name] = max(table_ranks.get(endpoint.table_name, 0), len(unique_models))
    for endpoint in all_endpoints:
        endpoint.rank = table_ranks[endpoint.table_name]
    for endpoint in all_endpoints:
        find_payload(endpoint.data_response, endpoint, endpoint_collection)


def find_payload(response: Response, endpoint: Endpoint, endpoints: EndpointCollection) -> None:
    schema = response.content_schema
    if not response.payload:
        return None  # TODO: response has no schema, is endpoint ignored?
    schema = response.payload.prop
    root_path = response.payload.path

    # response_props = set(response.content_schema.crawlepd_properties.all_properties)
    response_props = set(schema.crawled_properties.all_properties)
    payload_props = set(response_props)

    for other in endpoints.all_endpoints_to_render:
        if other.path == endpoint.path:
            continue
        other_payload = other.data_response.payload
        if not other_payload:
            continue
        other_schema = other_payload.prop
        other_props = set(other_schema.crawled_properties)  # type: ignore[call-overload]

        # Remove all common props from the payload, assume most of those are metadata
        common_props = response_props & other_props
        # remaining_props = response_props - common_props
        # remaining props including their ancestry starting at top level parents
        new_props = payload_props - common_props
        # # Check if new props contain any object type props
        # has_object_props = any(
        #     prop_path in schema.crawled_properties.object_properties
        #     or prop_path in schema.crawled_properties.list_properties
        #     for prop_path in new_props
        # )
        # if len(new_props) == 1:
        #     prop_obj = schema.crawled_properties[list(new_props)[0]]
        #     if not prop_obj.is_object and not prop_obj.is_list:
        #         new_props.add(())

        if not new_props:
            # Don't remove all props
            continue
        payload_props = new_props

    payload_path: Tuple[str, ...] = ()

    if len(payload_props) == 1:
        # When there's only one remaining prop it can mean the payload is just
        # very similar to another endpoint.
        prop_path = list(payload_props)[0]
        if len(prop_path) > 0:
            payload_schema = schema.crawled_properties[prop_path]
            if not payload_schema.is_object and not payload_schema.is_list:
                prop_path = tuple(list(prop_path)[:-1])
                payload_path = prop_path  # type: ignore[assignment]

    if not payload_path:
        # Payload path is the deepest nested parent of all remaining props
        payload_path = find_longest_common_prefix(list(payload_props))

    payload_schema = schema.crawled_properties[payload_path]
    ret = DataPropertyPath(root_path + payload_path, payload_schema)
    print(endpoint.path)
    print(ret.path)
    print(ret.prop.name)
    print("---")
    response.payload = ret


def _process_response_list(
    response: Response,
    endpoint: Endpoint,
    endpoints: EndpointCollection,
) -> None:
    if not response.list_properties:
        return
    if () in response.list_properties:  # Response is a top level list
        response.list_property = DataPropertyPath((), response.list_properties[()])
        return

    level_counts = count_by_length(response.list_properties.keys())

    # Get list properties max 2 levels down
    props_first_levels = [
        (path, prop) for path, prop in sorted(response.list_properties.items(), key=lambda k: len(k)) if len(path) <= 2
    ]

    # If there is only one list property 1 or 2 levels down, this is the list
    for path, prop in props_first_levels:
        if not prop.is_object:  # Only looking for object lists
            continue
        levels = len(path)
        if level_counts[levels] == 1:
            response.list_property = DataPropertyPath(path, prop)
    parent = endpoints.find_immediate_parent(endpoint.path)
    if parent and not parent.required_parameters:
        response.list_property = None
