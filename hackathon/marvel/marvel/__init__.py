import hashlib
import time
from typing import Any, Dict, List, Tuple

import dlt
from dlt.extract.source import DltResource
from dlt.sources.helpers.rest_client.auth import APIKeyAuth
from rest_api import rest_api_source
from rest_api.typing import RESTAPIConfig


def get_auth_params(public_key: str, private_key: str) -> Tuple[int, Dict[str, str]]:
    ts = int(time.time())
    client_hash = hashlib.md5()
    client_hash.update(f"{ts}{private_key}{public_key}".encode())
    return {"ts": ts, "hash": client_hash.hexdigest()}


@dlt.source(name="marvel_source", max_table_nesting=2)
def marvel_source(
    base_url: str = dlt.config.value,
    public_key: str = dlt.secrets.value,
    private_key: str = dlt.secrets.value,
) -> List[DltResource]:
    # source configuration
    auth_params = get_auth_params(public_key, private_key)
    source_config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
            "paginator": {
                "type": "offset",
                "limit": 20,
                "offset_param": "offset",
                "limit_param": "limit",
                "total_path": "",
                "maximum_offset": 20,
            },
            "auth": APIKeyAuth(
                api_key=public_key,
                name="apikey",
                location="query",
            ),
        },
        "resource_defaults": {
            "endpoint": {
                "params": auth_params,
            }
        },
        "resources": [
            {
                "name": "get_characters",
                "table_name": "characters",
                "endpoint": {
                    "data_selector": "$.data.results",
                    "path": "/v1/public/characters",
                    "params": auth_params,
                },
            },
            {
                "name": "get_character_individual",
                "table_name": "character_details",
                "endpoint": {
                    "data_selector": "$.data.results",
                    "path": "/v1/public/characters/{characterId}",
                    "params": {
                        "characterId": {
                            "type": "resolve",
                            "resource": "get_characters",
                            "field": "id",
                        },
                        **auth_params,
                    },
                },
            },
            {
                "name": "get_comics_collection",
                "table_name": "comics",
                "endpoint": {
                    "data_selector": "$.data.results",
                    "path": "/v1/public/comics",
                    "params": {
                        **auth_params,
                        "modifiedSince": {
                            "type": "incremental",
                            "cursor_path": "modified",
                            "initial_value": "2010-08-21T17:11:27-0400"
                        }
                        # "format": "FILL_ME_IN", # TODO: fill in query parameter
                        # "formatType": "FILL_ME_IN", # TODO: fill in query parameter
                        # "noVariants": "FILL_ME_IN", # TODO: fill in query parameter
                        # "dateDescriptor": "FILL_ME_IN", # TODO: fill in query parameter
                        # "dateRange": "FILL_ME_IN", # TODO: fill in query parameter
                        # "title": "FILL_ME_IN", # TODO: fill in query parameter
                        # "titleStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "issueNumber": "FILL_ME_IN", # TODO: fill in query parameter
                        # "diamondCode": "FILL_ME_IN", # TODO: fill in query parameter
                        # "digitalId": "FILL_ME_IN", # TODO: fill in query parameter
                        # "upc": "FILL_ME_IN", # TODO: fill in query parameter
                        # "isbn": "FILL_ME_IN", # TODO: fill in query parameter
                        # "ean": "FILL_ME_IN", # TODO: fill in query parameter
                        # "issn": "FILL_ME_IN", # TODO: fill in query parameter
                        # "hasDigitalIssue": "FILL_ME_IN", # TODO: fill in query parameter
                        # "modifiedSince": "FILL_ME_IN", # TODO: fill in query parameter
                        # "creators": "FILL_ME_IN", # TODO: fill in query parameter
                        # "characters": "FILL_ME_IN", # TODO: fill in query parameter
                        # "series": "FILL_ME_IN", # TODO: fill in query parameter
                        # "events": "FILL_ME_IN", # TODO: fill in query parameter
                        # "stories": "FILL_ME_IN", # TODO: fill in query parameter
                        # "sharedAppearances": "FILL_ME_IN", # TODO: fill in query parameter
                        # "collaborators": "FILL_ME_IN", # TODO: fill in query parameter
                        # "orderBy": "FILL_ME_IN", # TODO: fill in query parameter
                        # "offset": "FILL_ME_IN", # TODO: fill in query parameter
                    },
                    "paginator": {
                        "type": "offset",
                        "limit": 20,
                        "offset_param": "offset",
                        "limit_param": "limit",
                        "total_path": "",
                        "maximum_offset": 20,
                    },
                },
            },
            {
                "name": "get_comic_individual",
                "table_name": "comic_details",
                "endpoint": {
                    "data_selector": "$.data.results",
                    "path": "/v1/public/comics/{comicId}",
                    "params": {
                        "comicId": {
                            "type": "resolve",
                            "resource": "get_comics_collection",
                            "field": "id",
                        },
                        **auth_params,
                    },
                },
            },
        ],
    }

    return rest_api_source(source_config)
