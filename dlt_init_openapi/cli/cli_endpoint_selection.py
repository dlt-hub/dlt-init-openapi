from typing import List, Set

import questionary

from dlt_init_openapi.parser.endpoints import Endpoint, EndpointCollection


def questionary_endpoint_selection(endpoints: EndpointCollection) -> Set[str]:
    """Endpoint selection with questionary. Returns a Set of endpoint names and a set of endpoints to deselect"""
    choices: List[questionary.Choice] = []
    prev_table_name = ""
    for endpoint in endpoints.all_endpoints_to_render:
        if prev_table_name != endpoint.detected_table_name:
            choices.append(questionary.Separator(f"\n{endpoint.detected_table_name} endpoints:\n"))
        prev_table_name = endpoint.detected_table_name
        text = [
            ("bold", str(endpoint.detected_resource_name)),
            ("italic", f" {endpoint.path}"),
        ]
        choices.append(questionary.Choice(text, endpoint))
    selected_endpoints: List[Endpoint] = questionary.checkbox(
        "Which resources would you like to generate? Press enter to continue, "
        + "if you do not select any resources, all of them will be rendered.",
        choices,
    ).ask()

    # return resource names of selected endpoints
    return {e.id for e in selected_endpoints}
