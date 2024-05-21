from typing import List

import dlt
from dlt.extract.source import DltResource
from rest_api import rest_api_source
from rest_api.typing import RESTAPIConfig


@dlt.source(name="hacker_news_source", max_table_nesting=2)
def hacker_news_source(
    base_url: str = dlt.config.value,
) -> List[DltResource]:

    # source configuration
    source_config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
        },
        "resources": [
            {
                "name": "item",
                "table_name": "item",
                "endpoint": {
                    "path": "/item/{id}.json",
                    "data_selector": "$",
                    "paginator": "single_page",
                    "params": {
                        "id": {
                            "type": "resolve",
                            "field": "$",
                            "resource": "topstory"
                        }
                    },
                },
            },
            {
                "name": "topstory",
                "table_name": "topstory",
                "endpoint": {
                    "path": "/topstories.json",
                },
            },
        ],
    }

    return rest_api_source(source_config)


@dlt.source(name="hacker_news_source", max_table_nesting=2)
def hacker_news_source_original(
    base_url: str = dlt.config.value,
) -> List[DltResource]:

    # source configuration
    source_config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
        },
        "resources": [
            {
                "name": "item",
                "table_name": "item",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/item/{id}.json",
                    "params": {
                        "id": "FILL_ME_IN",  # TODO: fill in path parameter
                    },
                },
            },
            {
                "name": "topstory",
                "table_name": "topstory",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/topstories.json",
                },
            },
        ],
    }

    return rest_api_source(source_config)
