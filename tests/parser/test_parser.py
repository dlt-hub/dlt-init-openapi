import pytest

from openapi_python_client.parser.openapi_parser import OpenapiParser
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


@pytest.mark.parametrize(
    "endpoint_path,payload_path,payload_name",
    [
        ("/browse/new-releases", ("albums", "items"), "SimplifiedAlbumObject"),
        # ("/playlists/{playlist_id}/tracks", ("items",), "PlaylistTrackObject"),
        ("/me/tracks", ("items", "[*]", "track"), "TrackObject"),
        ("/me/albums", ("items", "[*]", "album"), "AlbumObject"),
        ("/artists/{id}/related-artists", ("artists",), "ArtistObject"),
        ("/browse/categories/{category_id}", (), "CategoryObject"),
    ],
)
def test_extract_payload_spotify(
    endpoint_path: str, payload_path: tuple[str], payload_name: str, spotify_parser: OpenapiParser
) -> None:
    endpoints = spotify_parser.endpoints

    endpoint = endpoints.endpoints_by_path[endpoint_path]

    assert endpoint.payload.path == payload_path
    assert endpoint.payload.name == payload_name


@pytest.mark.parametrize(
    "endpoint_path,payload_path,payload_name",
    [
        ("/api/v2/pokemon/{id}/", (), "Pokemon"),
        ("/api/v2/pokemon-species/", ("results",), "PokemonSpecies"),
        ("/api/v2/egg-group/", (), "EggGroup"),
    ],
)
def test_extract_payload_pokeapi(
    endpoint_path: str, payload_path: tuple[str], payload_name: str, pokemon_parser: OpenapiParser
) -> None:
    endpoints = pokemon_parser.endpoints

    endpoint = endpoints.endpoints_by_path[endpoint_path]

    assert endpoint.payload.path == payload_path
    assert endpoint.payload.name == payload_name


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


def test_parent_endpoints(spotify_parser: OpenapiParser) -> None:
    # TODO: test e.g. /browse/categories -> /browse/categories/{category_id}/playlists
    parent_path = "/browse/categories"
    child_path = "/browse/categories/{category_id}/playlists"

    parent = spotify_parser.endpoints.endpoints_by_path[parent_path]
    child = spotify_parser.endpoints.endpoints_by_path[child_path]

    assert child.parent is parent


def test_schema_name(spotify_parser: OpenapiParser) -> None:
    path = "/me/albums"
    endpoint = spotify_parser.endpoints.endpoints_by_path[path]

    schema = endpoint.data_response.content_schema

    album_schema = schema["items"].schema.array_item["album"].schema
    # Name taken from nested schema in all_of
    assert album_schema.name == "AlbumObject"


def test_detect_primary_key(pokemon_parser: OpenapiParser) -> None:
    path = "/api/v2/egg-group/"
    endpoint = pokemon_parser.endpoints.endpoints_by_path[path]

    assert endpoint.primary_key == "id"
