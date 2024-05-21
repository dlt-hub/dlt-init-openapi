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
            "paginator": {
                "type": "offset",
                "limit": 20,
                "offset_param": "offset",
                "limit_param": "limit",
                "total_path": "count",
            },
        },
        "resources": [
            {
                "name": "pokemon_list",
                "table_name": "pokemon",
                "primary_key": "id",
                "write_disposition": "merge",
                "endpoint": {
                    "data_selector": "results",
                    "path": "/api/v2/pokemon/",
                },
            },
            {
                "name": "pokemon_read",
                "table_name": "pokemon",
                "primary_key": "id",
                "write_disposition": "merge",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/api/v2/pokemon/{name}/",
                    "params": {
                        "name": {
                            "type": "resolve",
                            "resource": "pokemon_list",
                            "field": "name",
                        },
                    },
                },
            },
        ],
    }

    return rest_api_source(source_config)
