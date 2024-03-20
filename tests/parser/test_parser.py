import pytest

from openapi_python_client.parser.openapi_parser import OpenapiParser
from openapi_schema_pydantic import Reference

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

    list_item_schema = list_prop.prop

    assert list_item_schema.name == "SimplifiedAlbumObject"
    assert list_item_schema.types == ["object"]
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

    assert new_releases_endpoint.data_response.payload.path == ("albums", "items", "[*]")
    assert new_releases_endpoint.data_response.payload.prop.name == "SimplifiedAlbumObject"

    assert pl_tr_endpoint.data_response.payload.path == ("items", "[*]")
    assert pl_tr_endpoint.data_response.payload.prop.name == "PlaylistTrackObject"

    assert saved_tracks_endpoint.data_response.payload.path == ("items", "[*]")
    assert saved_tracks_endpoint.data_response.payload.prop.name == "SavedTrackObject"

    assert related_artists_endpoint.data_response.payload.path == ("artists", "[*]")
    assert related_artists_endpoint.data_response.payload.prop.name == "ArtistObject"


def test_find_path_param(pokemon_parser: OpenapiParser) -> None:
    endpoints = pokemon_parser.endpoints
    endpoint = endpoints.endpoints_by_path["/api/v2/pokemon-species/"]

    schema = endpoint.payload.prop
    result = schema.crawled_properties.find_property_by_name("id", fallback="id")

    assert result.path == ("[*]", "id")
