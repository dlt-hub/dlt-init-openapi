from dataclasses import dataclass
from typing import Any, List, Literal, Optional, Union, cast

import openapi_schema_pydantic as osp

from dlt_init_openapi.parser.context import OpenapiContext
from dlt_init_openapi.parser.models import DataPropertyPath, SchemaWrapper, TSchemaType
from dlt_init_openapi.parser.types import compare_openapi_types

TParamIn = Literal["query", "header", "path", "cookie"]


@dataclass
class Parameter:
    name: str
    description: Optional[str]
    schema: SchemaWrapper
    osp_parameter: osp.Parameter
    required: bool
    location: TParamIn
    style: Optional[str] = None

    @property
    def types(self) -> List[TSchemaType]:
        return self.schema.types

    @property
    def type_format(self) -> Optional[str]:
        return self.schema.type_format

    @property
    def default(self) -> Optional[Any]:
        return self.schema.default

    @property
    def nullable(self) -> bool:
        return self.schema.nullable

    @property
    def maximum(self) -> Optional[float]:
        return self.schema.maximum

    def _matches_type(self, schema: SchemaWrapper) -> bool:
        return compare_openapi_types(self.types, self.type_format, schema.types, schema.type_format)

    def find_input_property(self, schema: SchemaWrapper, fallback: Optional[str] = None) -> Optional[DataPropertyPath]:
        """Find property in the given schema that's potentially an input to this parameter
        TODO: improve heuristics, move this into some utility function for easy testing
        """
        prop = None
        for p in schema.properties:
            if p.name == self.name:
                prop = p
                break
            if p.name == fallback:
                prop = p
        if prop:
            return DataPropertyPath((prop.name,), prop.schema)
        return None

    @classmethod
    def from_reference(cls, param_ref: Union[osp.Reference, osp.Parameter], context: OpenapiContext) -> "Parameter":
        osp_parameter = context.parameter_from_reference(param_ref)

        # if there is no schema attached, fall back to string
        if not osp_parameter.param_schema:
            osp_parameter.param_schema = osp.Schema(type="string")

        schema = SchemaWrapper.from_reference(osp_parameter.param_schema, context)
        description = param_ref.description or osp_parameter.description or schema.description
        location = osp_parameter.param_in
        required = osp_parameter.required

        return cls(
            name=osp_parameter.name,
            description=description,
            osp_parameter=osp_parameter,
            schema=schema,
            location=cast(TParamIn, location),
            required=required,
            style=osp_parameter.style,
        )
