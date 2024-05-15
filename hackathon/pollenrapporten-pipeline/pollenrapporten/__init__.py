from typing import List

import dlt
from dlt.extract.source import DltResource
from rest_api import rest_api_source
from rest_api.typing import RESTAPIConfig


@dlt.source(name="pollenrapporten_source", max_table_nesting=2)
def pollenrapporten_source(
    base_url: str = dlt.config.value,
) -> List[DltResource]:

    # source configuration
    source_config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
        },
        "resources": [
            {
                "name": "pollen_types",
                "table_name": "pagination_link",
                "endpoint": {
                    "data_selector": "_links",
                    "path": "/v1/pollen-types",
                    "paginator": {
                        "type": "offset",
                        "limit": 100,
                        "offset_param": "offset",
                        "limit_param": "limit",
                        "total_path": "_meta.totalRecords",
                    },
                },
            },
            {
                "name": "pollen_level_definitions",
                "table_name": "pagination_link",
                "endpoint": {
                    "data_selector": "_links",
                    "path": "/v1/pollen-level-definitions",
                    "paginator": {
                        "type": "offset",
                        "limit": 100,
                        "offset_param": "offset",
                        "limit_param": "limit",
                        "total_path": "_meta.totalRecords",
                    },
                },
            },
            {
                "name": "regions",
                "table_name": "pagination_link",
                "endpoint": {
                    "data_selector": "_links",
                    "path": "/v1/regions",
                    "paginator": {
                        "type": "offset",
                        "limit": 100,
                        "offset_param": "offset",
                        "limit_param": "limit",
                        "total_path": "_meta.totalRecords",
                    },
                },
            },
            {
                "name": "forecasts",
                "table_name": "pagination_link",
                "endpoint": {
                    "data_selector": "_links",
                    "path": "/v1/forecasts",
                    "paginator": {
                        "type": "offset",
                        "limit": 100,
                        "offset_param": "offset",
                        "limit_param": "limit",
                        "total_path": "_meta.totalRecords",
                    },
                },
            },
            {
                "name": "pollen_count",
                "table_name": "pagination_link",
                "endpoint": {
                    "data_selector": "_links",
                    "path": "/v1/pollen-count",
                    "paginator": {
                        "type": "offset",
                        "limit": 100,
                        "offset_param": "offset",
                        "limit_param": "limit",
                        "total_path": "_meta.totalRecords",
                    },
                },
            },
        ],
    }

    return rest_api_source(source_config)
