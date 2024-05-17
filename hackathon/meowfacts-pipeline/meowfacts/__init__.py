from typing import List

import dlt
from dlt.extract.source import DltResource
from rest_api import rest_api_source
from rest_api.typing import RESTAPIConfig


@dlt.source(name="meowfacts_source", max_table_nesting=2)
def meowfacts_source(
    base_url: str = dlt.config.value,
) -> List[DltResource]:

    # source configuration
    source_config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
        },
        "resources": [
            {
                "name": "healthcheck_data",
                "table_name": "healthcheck_data",
                "endpoint": {
                    "data_selector": "data",
                    "path": "/health",
                },
            },
        ],
    }

    return rest_api_source(source_config)
