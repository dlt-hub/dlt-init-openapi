from typing import List

import dlt
from dlt.extract.source import DltResource
from rest_api import rest_api_source
from rest_api.typing import RESTAPIConfig


@dlt.source(name="ratp_source", max_table_nesting=2)
def ratp_source(
    api_key: str = dlt.secrets.value,
    base_url: str = dlt.config.value,
) -> List[DltResource]:

    # source configuration
    source_config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
            "auth": {"type": "api_key", "api_key": api_key, "name": "apikey", "location": "header"},
        },
        "resources": [
            {
                "name": "get_datasets",
                "table_name": "dataset",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/catalog/datasets",
                    "paginator": {
                        "type": "offset",
                        "limit": 100,
                        "offset_param": "offset",
                        "limit_param": "limit",
                        "maximum_offset": 20,
                    },
                },
            },
            {
                "name": "get_records",
                "table_name": "record",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/catalog/datasets/{dataset_id}/records",
                    "params": {
                        "dataset_id": "FILL_ME_IN",  # TODO: fill in required path parameter
                    },
                    "paginator": {
                        "type": "offset",
                        "limit": 100,
                        "offset_param": "offset",
                        "limit_param": "limit",
                        "maximum_offset": 20,
                    },
                },
            },
            {
                "name": "get_record",
                "table_name": "record",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/catalog/datasets/{dataset_id}/records/{record_id}",
                    "params": {
                        "dataset_id": "FILL_ME_IN",  # TODO: fill in required path parameter
                        "record_id": "FILL_ME_IN",  # TODO: fill in required path parameter
                    },
                },
            },
        ],
    }

    return rest_api_source(source_config)
