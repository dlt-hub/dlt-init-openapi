from typing import List

import dlt
from dlt.extract.source import DltResource
from rest_api import rest_api_source
from rest_api.typing import RESTAPIConfig


@dlt.source(name="star_trek_source", max_table_nesting=2)
def star_trek_source(
    base_url: str = dlt.config.value,
) -> List[DltResource]:

    # source configuration
    source_config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
        },
        "resources": [
            {
                "name": "v1_rest_season_search",
                "table_name": "season_base",
                "primary_key": "uid",
                "write_disposition": "merge",
                "endpoint": {
                    "data_selector": "seasons",
                    "path": "/v1/rest/season/search",
                    "paginator": {
                        "type": "page_number",
                        "page_param": "pageNumber",
                        "total_path": "page.totalElements",
                    },
                },
            },
        ],
    }

    return rest_api_source(source_config)
