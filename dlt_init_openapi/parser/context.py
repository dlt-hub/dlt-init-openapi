from typing import Any, Dict, Optional, Tuple, Union

import openapi_schema_pydantic as osp
import referencing
import referencing.jsonschema

from dlt_init_openapi.parser.config import Config

TComponentClass = Union[
    osp.Schema,
    osp.Parameter,
    osp.Response,
    osp.Header,
    osp.Example,
    osp.Link,
    osp.SecurityScheme,
    osp.RequestBody,
]


class OpenapiContext:
    spec: osp.OpenAPI
    spec_raw: Dict[str, Any]
    config: Config

    _component_cache: Dict[str, Dict[str, Any]] = {}

    def __init__(self, config: Config, spec: osp.OpenAPI, spec_raw: Dict[str, Any]) -> None:
        self.config = config
        self.spec = spec
        self.spec_raw = spec_raw

        # setup ref resolver
        resource = referencing.Resource(  # type: ignore[var-annotated, call-arg]
            contents=self.spec_raw, specification=referencing.jsonschema.DRAFT202012
        )
        registry = referencing.Registry().with_resource(resource=resource, uri="")
        self._resolver = registry.resolver()

    def _component_from_reference_url(self, url: str) -> Dict[str, Any]:
        if url in self._component_cache:
            return self._component_cache[url]
        obj = self._resolver.lookup(url).contents
        self._component_cache[url] = obj
        return obj

    def _component_from_reference(self, ref: osp.Reference) -> Dict[str, Any]:
        url = ref.ref
        return self._component_from_reference_url(url)

    def schema_and_name_from_reference(self, ref: Union[osp.Reference, osp.Schema]) -> Tuple[str, osp.Schema]:
        name: Optional[str] = None
        if isinstance(ref, osp.Reference):
            if ref.ref.startswith("#/components/"):
                # Refs to random places in the spec, e.g. #/paths/some~path/responses/.../schema
                # don't generate useful names, so only take names from #/components/schemas/SchemaName refs
                name = ref.ref.split("/components/")[-1].split("/")[-1]
            else:
                name = ""
        schema = self.schema_from_reference(ref)
        name = name or schema.title
        return name, schema

    def response_from_reference(self, ref: Union[osp.Reference, osp.Response]) -> osp.Response:
        if isinstance(ref, osp.Response):
            return ref
        return osp.Response.parse_obj(self._component_from_reference(ref))

    def schema_from_reference(self, ref: Union[osp.Reference, osp.Schema]) -> osp.Schema:
        if isinstance(ref, osp.Schema):
            return ref
        return osp.Schema.parse_obj(self._component_from_reference(ref))

    def parameter_from_reference(self, ref: Union[osp.Reference, osp.Parameter]) -> osp.Parameter:
        if isinstance(ref, osp.Parameter):
            return ref
        return osp.Parameter.parse_obj(self._component_from_reference(ref))
