from typing import List, Set

import questionary

from openapi_python_client.parser.endpoints import Endpoint, EndpointCollection


def questionary_endpoint_selection(endpoints: EndpointCollection) -> Set[str]:
    """Endpoint selection with questionary. Returns a Set of endpoint names"""
    choices: List[questionary.Choice] = []
    prev_resource_name = ""
    for endpoint in endpoints.all_endpoints_to_render:
        if prev_resource_name != endpoint.detected_resource_name:
            choices.append(questionary.Separator(f"\n{endpoint.detected_resource_name} endpoints:\n"))
        prev_resource_name = endpoint.detected_resource_name
        text = [
            ("bold", str(endpoint.operation_id)),
            ("italic", f" {endpoint.path}"),
        ]
        choices.append(questionary.Choice(text, endpoint))
    if not choices:
        raise ValueError("No endpoints found")
    selected_endpoints: List[Endpoint] = questionary.checkbox(
        "Which resources would you like to generate?", choices
    ).ask()

    selected_names = set()
    for ep in selected_endpoints:
        selected_names.add(str(ep.operation_id))
        if ep.transformer and ep.parent:
            # TODO: Generalize traversing ancestry chain
            selected_names.add(str(ep.parent.operation_id))
    return selected_names
