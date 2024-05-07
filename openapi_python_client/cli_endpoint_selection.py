from typing import List, Set, Tuple

import questionary

from openapi_python_client.parser.endpoints import Endpoint, EndpointCollection


def questionary_endpoint_selection(endpoints: EndpointCollection) -> Tuple[Set[str], Set[str]]:
    """Endpoint selection with questionary. Returns a Set of endpoint names and a set of endpoints to deselect"""
    choices: List[questionary.Choice] = []
    prev_table_name = ""
    for endpoint in endpoints.all_endpoints_to_render:
        if prev_table_name != endpoint.detected_table_name:
            choices.append(questionary.Separator(f"\n{endpoint.detected_resource_name} endpoints:\n"))
        prev_table_name = endpoint.detected_table_name
        text = [
            ("bold", str(endpoint.detected_resource_name)),
            ("italic", f" {endpoint.path}"),
        ]
        choices.append(questionary.Choice(text, endpoint))
    if not choices:
        raise ValueError("No endpoints found")
    selected_endpoints: List[Endpoint] = questionary.checkbox(
        "Which resources would you like to generate?", choices
    ).ask()

    # traverse ancestry chain and find all parents that also need to be rendered
    selected_names = set()
    render_names = set()
    for ep in selected_endpoints:
        render_names.add(ep.detected_resource_name)
        selected_names.add(ep.detected_resource_name)
        while ep.transformer and ep.parent:
            render_names.add(ep.parent.detected_resource_name)
            ep = ep.parent

    # we also need to mark the resources that should be rendered, but marked as deselected
    # this is the second var
    return render_names, (render_names - selected_names)
