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

    def get_imports(self) -> List[str]:
        imports = []
        if self.schema.is_union:
            imports.append("from typing import Union")
        return imports

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

    def to_docstring(self) -> str:
        doc = f"{self.python_name}: {self.description or ''}"
        if self.default:
            doc += f" Default: {self.default}."
        # TODO: Example
        return doc

    def _matches_type(self, schema: SchemaWrapper) -> bool:
        return compare_openapi_types(self.types, self.type_format, schema.types, schema.type_format)

    def find_input_property(self, schema: SchemaWrapper, fallback: Optional[str] = None) -> Optional[DataPropertyPath]:
        """Find property in the given schema that's potentially an input to this parameter"""
        name = self.name
        named = []
        fallbacks = []
        named_optional = []
        fallbacks_optional = []
        partial_named = []
        partial_named_optional = []
        partial_fallbacks = []
        partial_fallbacks_optional = []

        for path, prop_schema in schema.crawled_properties.items():
            if path and path[-1] == name:
                if not self._matches_type(prop_schema):
                    continue
                if schema.crawled_properties.is_optional(path):
                    named_optional.append((path, prop_schema))
                else:
                    named.append((path, prop_schema))
            if fallback and path and path[-1] == fallback:
                if not self._matches_type(prop_schema):
                    continue
                if schema.crawled_properties.is_optional(path):
                    fallbacks_optional.append((path, prop_schema))
                else:
                    fallbacks.append((path, prop_schema))
            # Check for partial name matches of the same type
            if path and name.lower() in path[-1].lower():
                if not self._matches_type(prop_schema):
                    continue
                if schema.crawled_properties.is_optional(path):
                    partial_named_optional.append((path, prop_schema))
                else:
                    partial_named.append((path, prop_schema))
            if fallback and path and fallback.lower() in path[-1].lower():
                if not self._matches_type(prop_schema):
                    continue
                if schema.crawled_properties.is_optional(path):
                    partial_fallbacks_optional.append((path, prop_schema))
                else:
                    partial_fallbacks.append((path, prop_schema))

        # Prefer the least nested path
        for arr in [
            named,
            fallbacks,
            named_optional,
            fallbacks_optional,
            partial_named,
            partial_fallbacks,
            partial_named_optional,
            partial_fallbacks_optional,
        ]:
            arr.sort(key=lambda item: len(item[0]))

        # Prefer required property and required fallback over optional properties
        # If not required props found, assume the spec is wrong and optional properties are required in practice
        # Partial name matches are least preferred
        if named:
            return DataPropertyPath(*named[0])
        elif fallbacks:
            return DataPropertyPath(*fallbacks[0])
        elif named_optional:
            return DataPropertyPath(*named_optional[0])
        elif fallbacks_optional:
            return DataPropertyPath(*fallbacks_optional[0])
        elif partial_named:
            return DataPropertyPath(*partial_named[0])
        elif partial_fallbacks:
            return DataPropertyPath(*partial_fallbacks[0])
        elif partial_named_optional:
            return DataPropertyPath(*partial_named_optional[0])
        elif partial_fallbacks_optional:
            return DataPropertyPath(*partial_fallbacks_optional[0])
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
