from typing import List

import dlt
from dlt.extract.source import DltResource

from rest_api import rest_api_source
from rest_api.typing import RESTAPIConfig


@dlt.source(name="coinbase_source", max_table_nesting=2)
def coinbase_source(
    base_url: str = dlt.config.value,
) -> List[DltResource]:

    # source configuration
    source_config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
        },
        "resources": [
            {
                "name": "get_asset_networks",
                "table_name": "asset_network_v_1",
                "primary_key": "asset_id",
                "write_disposition": "merge",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/api/v1/assets/{asset}/networks",
                    "params": {
                        "asset": {
                            "type": "resolve",
                            "resource": "get_assets",
                            "field": "asset_id",
                        },
                    },
                },
            },
            {
                "name": "get_assets",
                "table_name": "asset_v_1",
                "primary_key": "asset_id",
                "write_disposition": "merge",
                "selected": False,
                "endpoint": {
                    "data_selector": "$",
                    "path": "/api/v1/assets",
                },
            },
        ],
    }

    return rest_api_source(source_config)
