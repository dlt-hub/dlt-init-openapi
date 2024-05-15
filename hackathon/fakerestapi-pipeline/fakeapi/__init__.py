from typing import List

import dlt
from dlt.extract.source import DltResource
from rest_api import rest_api_source
from rest_api.typing import RESTAPIConfig


@dlt.source(name="fakeapi_source", max_table_nesting=2)
def fakeapi_source(
    base_url: str = dlt.config.value,
) -> List[DltResource]:
    # source configuration
    source_config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
        },
        "resources": [
            {
                "name": "list_activities",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/api/v1/Activities",
                },
            },
            {
                "name": "list_authors",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/api/v1/Authors",
                },
            },
            {
                "name": "list_books",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/api/v1/Books",
                },
            },
            {
                "name": "get_book_by_author",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/api/v1/Authors/authors/books/{idBook}",
                    "params": {
                        "idBook": {
                            "type": "resolve",
                            "resource": "list_books",
                            "field": "id"
                        }
                    },
                },
            },
        ],
    }

    return rest_api_source(source_config)
