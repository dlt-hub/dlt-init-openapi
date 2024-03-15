from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from openapi_python_client.parser.models import SchemaWrapper, Property


TOpenApiType = Literal["boolean", "object", "array", "number", "string", "integer"]

OATypeToPyType = {"boolean": "bool", "number": "float", "string": "str", "integer": "int"}


def schema_to_type_hint(schema: SchemaWrapper, required: bool = True) -> str:
    types = schema.types
    nullable = schema.nullable or not required
    tpl = "Optional[{}]" if nullable else "{}"
    union_types: Dict[str, None] = {}  # Using a dict as a faux ordered set (for deterministic client code)
    for s_type in types:
        py_type = OATypeToPyType.get(s_type)
        if py_type:
            union_types[py_type] = None
            continue
        elif s_type == "object":
            union_types["Dict[str, Any]"] = None
        elif s_type == "array":
            item_type = schema_to_type_hint(schema.array_item)
            py_type = f"List[{item_type}]"
            union_types[py_type] = None
    for one_of in schema.one_of + schema.any_of:
        union_types[schema_to_type_hint(one_of)] = None

    final_type = ""
    if len(union_types) == 1:
        final_type = next(iter(union_types))
    elif len(union_types) == 0:
        final_type = "Any"
    else:
        final_type = ", ".join(union_types)
    return tpl.format(final_type)


@dataclass
class DataType:
    type_hint: str

    @classmethod
    def from_schema(cls, schema: "SchemaWrapper", required: bool = True) -> "DataType":
        return cls(type_hint=schema_to_type_hint(schema, required=required))

    @classmethod
    def from_property(cls, prop: "Property") -> "DataType":
        """Create a DataType from a Property.
        Properties may be required or not, so we need to pass that information."""
        return cls(type_hint=schema_to_type_hint(prop.schema, required=prop.required))
