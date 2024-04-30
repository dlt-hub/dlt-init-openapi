from dataclasses import dataclass
from typing import Any, List, Literal, Optional, Union, cast

import openapi_schema_pydantic as osp

from openapi_python_client.utils import PythonIdentifier
from openapi_python_client.parser.models import SchemaWrapper, TSchemaType, DataPropertyPath
from openapi_python_client.parser.types import DataType, compare_openapi_types
from openapi_python_client.parser.context import OpenapiContext

TParamIn = Literal["query", "header", "path", "cookie"]


@dataclass
class Parameter:
    name: str
    description: Optional[str]
    schema: SchemaWrapper
    raw_schema: osp.Parameter
    required: bool
    location: TParamIn
    python_name: PythonIdentifier
    explode: bool
    style: Optional[str] = None

    @property
    def types(self) -> List[TSchemaType]:
        return self.schema.types

    @property
    def type_format(self) -> Optional[str]:
        return self.schema.type_format

    @property
    def template(self) -> str:
        return self.schema.property_template

    @property
    def default(self) -> Optional[Any]:
        return self.schema.default

    @property
    def nullable(self) -> bool:
        return self.schema.nullable

    @property
    def maximum(self) -> Optional[float]:
        return self.schema.maximum

    @property
    def type_hint(self) -> str:
        return DataType.from_schema(self.schema, required=self.required).type_hint

    def to_string(self) -> str:
        type_hint = self.type_hint
        default = self.default
        if default is None and not self.required:
            default = "UNSET"

        base_string = f"{self.python_name}: {type_hint}"
        if default is not None:
            base_string += f" = {default}"
        return base_string

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
        osp_param = context.parameter_from_reference(param_ref)
        schema = SchemaWrapper.from_reference(osp_param.param_schema, context)
        description = param_ref.description or osp_param.description or schema.description
        location = osp_param.param_in
        required = osp_param.required

        return cls(
            name=osp_param.name,
            description=description,
            raw_schema=osp_param,
            schema=schema,
            location=cast(TParamIn, location),
            required=required,
            python_name=PythonIdentifier(osp_param.name, prefix=context.config.field_prefix),
            explode=osp_param.explode or False,
            style=osp_param.style,
        )
