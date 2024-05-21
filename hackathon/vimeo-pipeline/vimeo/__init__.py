from typing import List

import dlt
from dlt.extract.source import DltResource

from rest_api import rest_api_source
from rest_api.typing import RESTAPIConfig


@dlt.source(name="vimeo_source", max_table_nesting=2)
def vimeo_source(
    base_url: str = dlt.config.value,
    token: str = dlt.secrets.value,
) -> List[DltResource]:

    # source configuration
    source_config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
            "paginator": {
                "type": "json_response",
            },
            "auth": {
                "token": token,
            }
        },
        "resources": [
            {
                "name": "get_categories",
                "table_name": "category",
                "primary_key": "uri",
                "write_disposition": "merge",
                "endpoint": {
                    #"data_selector": "$",
                    "path": "/categories",
                    "params": {
                        # "direction": "FILL_ME_IN", # TODO: fill in query parameter
                        # "per_page": "FILL_ME_IN", # TODO: fill in query parameter
                        # "sort": "FILL_ME_IN", # TODO: fill in query parameter
                    },
                },
            },
            {
                "name": "get_category",
                "table_name": "category",
                "primary_key": "uri",
                "write_disposition": "merge",
                "endpoint": {
                    "data_selector": "$",
                    "path": "{category}",
                    "params": {
                        "category": {
                            "type": "resolve",
                            "resource": "get_categories",
                            "field": "uri",
                        },
                    },
                },
            },
        ],
    }

    return rest_api_source(source_config)
