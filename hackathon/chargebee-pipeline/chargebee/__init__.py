from typing import List

import dlt
from dlt.extract.source import DltResource
from rest_api import rest_api_source
from rest_api.typing import RESTAPIConfig


@dlt.source(name="chargebee_source", max_table_nesting=2)
def chargebee_source(
    api_token: str = dlt.secrets.value,
    password: str = dlt.secrets.value,
    base_url: str = dlt.config.value,
) -> List[DltResource]:

    # source configuration
    source_config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
            "auth": {
                "type": "http_basic",
                "username": api_token,
                "password": password,
            },
        },
        "resources": [
            {
                "name": "list_customers",
                "table_name": "customer",
                "endpoint": {
                    "data_selector": "list",
                    "path": "/customers",
                    "paginator": {
                        "type": "offset",
                        "limit": 100,
                        "offset_param": "next_offset",
                        "limit_param": "limit",
                        "maximum_offset": 20,
                    },
                },
            },
        ],
    }

    return rest_api_source(source_config)
