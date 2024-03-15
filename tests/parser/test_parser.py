from openapi_python_client.parser.openapi_parser import OpenapiParser
from openapi_schema_pydantic import Reference

from tests.cases import case_path


def test_openapi_parser() -> None:
    parser = OpenapiParser(case_path("spotify.json"))

    parser.parse()

    endpoints = parser.endpoints.endpoints_by_path

    endpoint = endpoints["/browse/new-releases"]

    list_prop = endpoint.list_property
    assert list_prop is not None

    assert list_prop.path == ("albums", "items")

    list_item_schema = list_prop.prop

    assert list_item_schema.name == "SimplifiedAlbumObject"
    assert list_item_schema.types == ["object"]
    prop_names = [p.name for p in list_item_schema.properties]
    assert "id" in prop_names
    assert "name" in prop_names
    assert "release_date" in prop_names
