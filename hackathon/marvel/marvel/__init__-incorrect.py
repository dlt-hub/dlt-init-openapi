from typing import List

import dlt
from dlt.extract.source import DltResource

from rest_api import rest_api_source
from rest_api.typing import RESTAPIConfig


@dlt.source(name="marvel_source", max_table_nesting=2)
def marvel_source(
    base_url: str = dlt.config.value,
) -> List[DltResource]:

    # source configuration
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
        },
        "resources": [
            {
                "name": "get_creator_collection",
                "table_name": "character",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/v1/public/characters",
                    "params": {
                        # "name": "FILL_ME_IN", # TODO: fill in query parameter
                        # "nameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "modifiedSince": "FILL_ME_IN", # TODO: fill in query parameter
                        # "comics": "FILL_ME_IN", # TODO: fill in query parameter
                        # "series": "FILL_ME_IN", # TODO: fill in query parameter
                        # "events": "FILL_ME_IN", # TODO: fill in query parameter
                        # "stories": "FILL_ME_IN", # TODO: fill in query parameter
                        # "orderBy": "FILL_ME_IN", # TODO: fill in query parameter
                    },
                },
            },
            {
                "name": "get_character_individual",
                "table_name": "character",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/v1/public/characters/{characterId}",
                    "params": {
                        "characterId": "FILL_ME_IN",  # TODO: fill in path parameter
                    },
                },
            },
            {
                "name": "get_creator_collection",
                "table_name": "character",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/v1/public/stories/{storyId}/characters",
                    "params": {
                        "storyId": "FILL_ME_IN",  # TODO: fill in path parameter
                        # "name": "FILL_ME_IN", # TODO: fill in query parameter
                        # "nameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "modifiedSince": "FILL_ME_IN", # TODO: fill in query parameter
                        # "comics": "FILL_ME_IN", # TODO: fill in query parameter
                        # "series": "FILL_ME_IN", # TODO: fill in query parameter
                        # "events": "FILL_ME_IN", # TODO: fill in query parameter
                        # "orderBy": "FILL_ME_IN", # TODO: fill in query parameter
                    },
                },
            },
            {
                "name": "get_comics_collection",
                "table_name": "comic",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/v1/public/comics",
                    "params": {
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
                        "offset_param": "startYear",
                        "limit_param": "limit",
                        "total_path": "",
                        "maximum_offset": 20,
                    },
                },
            },
            {
                "name": "get_comic_individual",
                "table_name": "comic",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/v1/public/comics/{comicId}",
                    "params": {
                        "comicId": "FILL_ME_IN",  # TODO: fill in path parameter
                    },
                },
            },
            {
                "name": "get_comics_collection",
                "table_name": "comic",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/v1/public/creators/{creatorId}/comics",
                    "params": {
                        "creatorId": "FILL_ME_IN",  # TODO: fill in path parameter
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
                        "offset_param": "startYear",
                        "limit_param": "limit",
                        "total_path": "",
                        "maximum_offset": 20,
                    },
                },
            },
            {
                "name": "get_comics_collection",
                "table_name": "comic",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/v1/public/events/{eventId}/comics",
                    "params": {
                        "eventId": "FILL_ME_IN",  # TODO: fill in path parameter
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
                        "offset_param": "startYear",
                        "limit_param": "limit",
                        "total_path": "",
                        "maximum_offset": 20,
                    },
                },
            },
            {
                "name": "get_comics_collection",
                "table_name": "comic",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/v1/public/series/{seriesId}/comics",
                    "params": {
                        "seriesId": "FILL_ME_IN",  # TODO: fill in path parameter
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
                        "offset_param": "startYear",
                        "limit_param": "limit",
                        "total_path": "",
                        "maximum_offset": 20,
                    },
                },
            },
            {
                "name": "get_comics_collection",
                "table_name": "comic",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/v1/public/stories/{storyId}/comics",
                    "params": {
                        "storyId": "FILL_ME_IN",  # TODO: fill in path parameter
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
                        # "sharedAppearances": "FILL_ME_IN", # TODO: fill in query parameter
                        # "collaborators": "FILL_ME_IN", # TODO: fill in query parameter
                        # "orderBy": "FILL_ME_IN", # TODO: fill in query parameter
                        # "offset": "FILL_ME_IN", # TODO: fill in query parameter
                    },
                    "paginator": {
                        "type": "offset",
                        "limit": 20,
                        "offset_param": "startYear",
                        "limit_param": "limit",
                        "total_path": "",
                        "maximum_offset": 20,
                    },
                },
            },
            {
                "name": "get_creator_collection",
                "table_name": "creator",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/v1/public/comics/{comicId}/creators",
                    "params": {
                        "comicId": "FILL_ME_IN",  # TODO: fill in path parameter
                        # "firstName": "FILL_ME_IN", # TODO: fill in query parameter
                        # "middleName": "FILL_ME_IN", # TODO: fill in query parameter
                        # "lastName": "FILL_ME_IN", # TODO: fill in query parameter
                        # "suffix": "FILL_ME_IN", # TODO: fill in query parameter
                        # "nameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "firstNameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "middleNameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "lastNameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "modifiedSince": "FILL_ME_IN", # TODO: fill in query parameter
                        # "comics": "FILL_ME_IN", # TODO: fill in query parameter
                        # "series": "FILL_ME_IN", # TODO: fill in query parameter
                        # "stories": "FILL_ME_IN", # TODO: fill in query parameter
                        # "orderBy": "FILL_ME_IN", # TODO: fill in query parameter
                    },
                },
            },
            {
                "name": "get_creator_collection",
                "table_name": "creator",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/v1/public/creators",
                    "params": {
                        # "firstName": "FILL_ME_IN", # TODO: fill in query parameter
                        # "middleName": "FILL_ME_IN", # TODO: fill in query parameter
                        # "lastName": "FILL_ME_IN", # TODO: fill in query parameter
                        # "suffix": "FILL_ME_IN", # TODO: fill in query parameter
                        # "nameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "firstNameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "middleNameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "lastNameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "modifiedSince": "FILL_ME_IN", # TODO: fill in query parameter
                        # "comics": "FILL_ME_IN", # TODO: fill in query parameter
                        # "series": "FILL_ME_IN", # TODO: fill in query parameter
                        # "events": "FILL_ME_IN", # TODO: fill in query parameter
                        # "stories": "FILL_ME_IN", # TODO: fill in query parameter
                        # "orderBy": "FILL_ME_IN", # TODO: fill in query parameter
                    },
                },
            },
            {
                "name": "get_creator_collection",
                "table_name": "creator",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/v1/public/events/{eventId}/creators",
                    "params": {
                        "eventId": "FILL_ME_IN",  # TODO: fill in path parameter
                        # "firstName": "FILL_ME_IN", # TODO: fill in query parameter
                        # "middleName": "FILL_ME_IN", # TODO: fill in query parameter
                        # "lastName": "FILL_ME_IN", # TODO: fill in query parameter
                        # "suffix": "FILL_ME_IN", # TODO: fill in query parameter
                        # "nameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "firstNameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "middleNameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "lastNameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "modifiedSince": "FILL_ME_IN", # TODO: fill in query parameter
                        # "comics": "FILL_ME_IN", # TODO: fill in query parameter
                        # "series": "FILL_ME_IN", # TODO: fill in query parameter
                        # "stories": "FILL_ME_IN", # TODO: fill in query parameter
                        # "orderBy": "FILL_ME_IN", # TODO: fill in query parameter
                    },
                },
            },
            {
                "name": "get_creator_collection",
                "table_name": "creator",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/v1/public/series/{seriesId}/creators",
                    "params": {
                        "seriesId": "FILL_ME_IN",  # TODO: fill in path parameter
                        # "firstName": "FILL_ME_IN", # TODO: fill in query parameter
                        # "middleName": "FILL_ME_IN", # TODO: fill in query parameter
                        # "lastName": "FILL_ME_IN", # TODO: fill in query parameter
                        # "suffix": "FILL_ME_IN", # TODO: fill in query parameter
                        # "nameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "firstNameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "middleNameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "lastNameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "modifiedSince": "FILL_ME_IN", # TODO: fill in query parameter
                        # "comics": "FILL_ME_IN", # TODO: fill in query parameter
                        # "events": "FILL_ME_IN", # TODO: fill in query parameter
                        # "stories": "FILL_ME_IN", # TODO: fill in query parameter
                        # "orderBy": "FILL_ME_IN", # TODO: fill in query parameter
                    },
                },
            },
            {
                "name": "get_creator_collection",
                "table_name": "creator",
                "endpoint": {
                    "data_selector": "$",
                    "path": "/v1/public/stories/{storyId}/creators",
                    "params": {
                        "storyId": "FILL_ME_IN",  # TODO: fill in path parameter
                        # "firstName": "FILL_ME_IN", # TODO: fill in query parameter
                        # "middleName": "FILL_ME_IN", # TODO: fill in query parameter
                        # "lastName": "FILL_ME_IN", # TODO: fill in query parameter
                        # "suffix": "FILL_ME_IN", # TODO: fill in query parameter
                        # "nameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "firstNameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "middleNameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "lastNameStartsWith": "FILL_ME_IN", # TODO: fill in query parameter
                        # "modifiedSince": "FILL_ME_IN", # TODO: fill in query parameter
                        # "comics": "FILL_ME_IN", # TODO: fill in query parameter
                        # "series": "FILL_ME_IN", # TODO: fill in query parameter
                        # "events": "FILL_ME_IN", # TODO: fill in query parameter
                        # "orderBy": "FILL_ME_IN", # TODO: fill in query parameter
                    },
                },
            },
        ],
    }

    return rest_api_source(source_config)
