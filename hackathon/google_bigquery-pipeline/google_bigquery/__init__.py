from typing import List

import dlt
from dlt.extract.source import DltResource

from rest_api import rest_api_source
from rest_api.typing import RESTAPIConfig


@dlt.source(name="google_bigquery_source", max_table_nesting=2)
def google_bigquery_source(
    base_url: str = dlt.config.value,
) -> List[DltResource]:

    # source configuration
    source_config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
            "paginator": {
                "type": "page_number",
                "page_param": "pageToken",
                "total_path": "",
                "maximum_page": 20,
            },
        },
        "resources": [
            {
                "name": "bigquery_datasets_list",
                "table_name": "dataset",
                "primary_key": "id",
                "write_disposition": "merge",
                "endpoint": {
                    "data_selector": "datasets",
                    "path": "/projects/{projectId}/datasets",
                    "params": {
                        "projectId": {
                            "type": "resolve",
                            "resource": "bigquery_projects_list",
                            "field": "id",
                        },
                        # "$.xgafv": "FILL_ME_IN", # TODO: fill in query parameter
                        # "access_token": "", # TODO: fill in query parameter
                        # "alt": "FILL_ME_IN", # TODO: fill in query parameter
                        # "callback": "FILL_ME_IN", # TODO: fill in query parameter
                        # "fields": "FILL_ME_IN", # TODO: fill in query parameter
                        # "key": "FILL_ME_IN", # TODO: fill in query parameter
                        # "oauth_token": "FILL_ME_IN", # TODO: fill in query parameter
                        # "prettyPrint": "FILL_ME_IN", # TODO: fill in query parameter
                        # "quotaUser": "FILL_ME_IN", # TODO: fill in query parameter
                        # "upload_protocol": "FILL_ME_IN", # TODO: fill in query parameter
                        # "uploadType": "FILL_ME_IN", # TODO: fill in query parameter
                        # "all": "FILL_ME_IN", # TODO: fill in query parameter
                        # "filter": "FILL_ME_IN", # TODO: fill in query parameter
                        # "maxResults": "FILL_ME_IN", # TODO: fill in query parameter
                    },
                },
            },
            {
                "name": "bigquery_projects_list",
                "table_name": "project",
                "primary_key": "id",
                "write_disposition": "merge",
                "selected": False,
                "endpoint": {
                    "data_selector": "projects",
                    "path": "/projects",
                    "params": {
                        # "$.xgafv": "FILL_ME_IN", # TODO: fill in query parameter
                        # "access_token": "", # TODO: fill in query parameter
                        # "alt": "FILL_ME_IN", # TODO: fill in query parameter
                        # "callback": "FILL_ME_IN", # TODO: fill in query parameter
                        # "fields": "FILL_ME_IN", # TODO: fill in query parameter
                        # "key": "FILL_ME_IN", # TODO: fill in query parameter
                        # "oauth_token": "FILL_ME_IN", # TODO: fill in query parameter
                        # "prettyPrint": "FILL_ME_IN", # TODO: fill in query parameter
                        # "quotaUser": "FILL_ME_IN", # TODO: fill in query parameter
                        # "upload_protocol": "FILL_ME_IN", # TODO: fill in query parameter
                        # "uploadType": "FILL_ME_IN", # TODO: fill in query parameter
                        # "maxResults": "FILL_ME_IN", # TODO: fill in query parameter
                    },
                    "paginator": {
                        "type": "page_number",
                        "page_param": "pageToken",
                        "total_path": "totalItems",
                    },
                },
            },
        ],
    }

    return rest_api_source(source_config)
