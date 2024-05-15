from typing import List

import dlt
from dlt.extract.source import DltResource
from rest_api import rest_api_source
from rest_api.typing import RESTAPIConfig


@dlt.source(name="fakerestapi_source", max_table_nesting=2)
def fakerestapi_source(
    base_url: str = dlt.config.value,
) -> List[DltResource]:
    # source configuration
    source_config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
        },
        "resources": [
            {
                "name": "get_apiv_1_activities",
                "table_name": "activity",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/api/v1/Activities",
                },
            },
            {
                "name": "get_apiv_1_activitiesid",
                "table_name": "activity",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/api/v1/Activities/{id}",
                    "params": {
                        "id": {
                            "type": "resolve",
                            "resource": "get_apiv_1_activities",
                            "field": "id",
                        }
                    },
                },
            },
            {
                "name": "get_apiv_1_authors",
                "table_name": "author",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/api/v1/Authors",
                },
            },
            {
                "name": "get_apiv_1_authorsid",
                "table_name": "author",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/api/v1/Authors/{id}",
                    "params": {
                        "id": {
                            "type": "resolve",
                            "resource": "get_apiv_1_authors",
                            "field": "id",
                        },
                    },
                },
            },
            {
                "name": "get_apiv_1_authorsauthorsbooksid_book",
                "table_name": "book",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/api/v1/Authors/authors/books/{idBook}",
                    "params": {
                        "idBook": {
                            "type": "resolve",
                            "resource": "get_apiv_1_books",
                            "field": "id",
                        },
                    },
                },
            },
            {
                "name": "get_apiv_1_books",
                "table_name": "book",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/api/v1/Books",
                },
            },
            {
                "name": "get_apiv_1_booksid",
                "table_name": "book",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/api/v1/Books/{id}",
                    "params": {
                        "id": {
                            "type": "resolve",
                            "resource": "get_apiv_1_books",
                            "field": "id",
                        },
                    },
                },
            },
        ],
    }

    return rest_api_source(source_config)
