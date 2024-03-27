import pytest

from openapi_python_client.parser.openapi_parser import OpenapiParser
from openapi_schema_pydantic import Reference
from openapi_python_client.parser.models import SchemaWrapper
import openapi_schema_pydantic as osp

from tests.cases import case_path


@pytest.fixture(scope="module")
def spotify_parser() -> OpenapiParser:
    """Re-use parsed spec to save time"""
    parser = OpenapiParser(case_path("spotify.json"))
    parser.parse()
    return parser


@pytest.fixture(scope="module")
def pokemon_parser() -> OpenapiParser:
    """Re-use parsed spec to save time"""
    parser = OpenapiParser(case_path("pokeapi.yml"))
    parser.parse()
    return parser


def test_new_releases_list_property(spotify_parser: OpenapiParser) -> None:
    endpoints = spotify_parser.endpoints.endpoints_by_path

    endpoint = endpoints["/browse/new-releases"]

    list_prop = endpoint.payload
    assert list_prop is not None

    assert list_prop.path == ("albums", "items")

    list_item_schema = list_prop.schema

    assert list_prop.name == "SimplifiedAlbumObject"
    assert list_prop.prop.array_item.types == ["object"]
    prop_names = [p.name for p in list_item_schema.properties]
    assert "id" in prop_names
    assert "name" in prop_names
    assert "release_date" in prop_names


# def test_spotify_single_item_endpoints(spotify_parser: OpenapiParser) -> None:
#     endpoint = spotify_parser.endpoints.endpoints_by_path["/albums/{id}"]

#     assert endpoint.is_transformer
#     schema = endpoint.data_response.content_schema


def test_extract_payload(spotify_parser: OpenapiParser) -> None:
    endpoints = spotify_parser.endpoints
    pl_tr_endpoint = endpoints.endpoints_by_path["/playlists/{playlist_id}/tracks"]
    new_releases_endpoint = endpoints.endpoints_by_path["/browse/new-releases"]
    saved_tracks_endpoint = endpoints.endpoints_by_path["/me/tracks"]
    related_artists_endpoint = endpoints.endpoints_by_path["/artists/{id}/related-artists"]

    assert new_releases_endpoint.data_response.payload.path == (
        "albums",
        "items",
    )
    assert new_releases_endpoint.data_response.payload.name == "SimplifiedAlbumObject"

    # TODO:
    # assert pl_tr_endpoint.data_response.payload.path == ("items",)
    # assert pl_tr_endpoint.data_response.payload.name == "PlaylistTrackObject"

    assert saved_tracks_endpoint.data_response.payload.path == ("items",)
    assert saved_tracks_endpoint.data_response.payload.name == "SavedTrackObject"

    assert related_artists_endpoint.data_response.payload.path == ("artists",)
    assert related_artists_endpoint.data_response.payload.name == "ArtistObject"


def test_find_path_param(pokemon_parser: OpenapiParser) -> None:
    endpoints = pokemon_parser.endpoints
    parent_endpoint = endpoints.endpoints_by_path["/api/v2/pokemon-species/"]
    endpoint = endpoints.endpoints_by_path["/api/v2/pokemon-species/{id}/"]

    schema = parent_endpoint.payload.prop
    param = endpoint.parameters["id"]
    result = param.find_input_property(schema, fallback="id")

    assert result.path == ("[*]", "id")


def test_schema_parse_types(pokemon_parser: OpenapiParser) -> None:
    osp_schema = osp.Schema.parse_obj(
        {
            "anyOf": [
                {"type": "string"},
                {"type": "null"},
            ],
            "title": "Pathname",
        }
    )

    parsed = SchemaWrapper.from_reference(osp_schema, context=pokemon_parser.context)

    assert parsed.nullable is True
    assert parsed.types == ["string"]


def test_resource_arguments(pokemon_parser: OpenapiParser) -> None:
    path = "/api/v2/pokemon-species/{id}/"
    endpoint = pokemon_parser.endpoints.endpoints_by_path[path]

    pos_args = endpoint.positional_arguments()

    # Does not include the id arg from transformer parent
    assert pos_args == []
