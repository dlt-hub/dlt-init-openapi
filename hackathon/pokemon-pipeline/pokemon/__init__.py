from typing import List

import dlt
from dlt.extract.source import DltResource
from rest_api import rest_api_source
from rest_api.typing import RESTAPIConfig


@dlt.source(name="pokemon_source", max_table_nesting=2)
def pokemon_source(
    base_url: str = dlt.config.value,
) -> List[DltResource]:

    # source configuration
    source_config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
        },
        "resources": [
            {
                "name": "ability_list",
                "table_name": "ability",
                "primary_key": "id",
                "write_disposition": "merge",
                "selected": False,
                "endpoint": {
                    "data_selector": "results",
                    "path": "/api/v2/ability/",
                    "paginator": {
                        "type": "offset",
                        "limit": 20,
                        "offset_param": "offset",
                        "limit_param": "limit",
                        "total_path": "count",
                    },
                },
            },
            {
                "name": "ability_read",
                "table_name": "ability",
                "primary_key": "id",
                "write_disposition": "merge",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/api/v2/ability/{id}/",
                    "params": {
                        "id": {
                            "type": "resolve",
                            "resource": "ability_list",
                            "field": "id",
                        },
                    },
                },
            },
        ],
    }

    return rest_api_source(source_config)
