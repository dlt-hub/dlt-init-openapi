from __future__ import annotations

import re
from dataclasses import dataclass, field
from itertools import chain
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Literal, Optional, Sequence, Tuple, TypeVar, Union, cast

import openapi_schema_pydantic as osp
from dlt.common.utils import digest128

from dlt_init_openapi.parser.types import DataType, TOpenApiType
from dlt_init_openapi.utils.misc import unique_list

if TYPE_CHECKING:
    from dlt_init_openapi.parser.context import OpenapiContext

from .const import MAX_RECURSION_DEPTH

TSchemaType = Literal["boolean", "object", "array", "number", "string", "integer"]


@dataclass
class DataPropertyPath:
    """Describes a json path to a property"""

    path: Tuple[str, ...]
    prop: "SchemaWrapper"  # TODO: Why is this not pointing to Property?

    @property
    def name(self) -> str:
        if self.is_list and self.prop.array_item:
            return self.prop.array_item.name
        return self.prop.name

    @property
    def json_path(self) -> str:
        return ".".join(self.path) if self.path else "$"

    @property
    def is_list(self) -> bool:
        return self.prop.is_list

    @property
    def schema(self) -> "SchemaWrapper":
        if self.is_list and self.prop.array_item:
            return self.prop.array_item
        return self.prop

    def __str__(self) -> str:
        return f"DataPropertyPath {self.path}: {self.prop.name}"


@dataclass
class SchemaWrapper:
    """Wraps an openapi Schema to add useful attributes and methods"""

    osp_schema: osp.Schema
    ref: Optional[osp.Reference]

    name: str
    """Name inferred from schema ref url or Schema.title property"""

    description: Optional[str]
    """Description from schema ref or schema.description property"""

    properties: List["Property"]

    types: List[TSchemaType]
    nullable: bool
    default: Optional[Any]
    """Default value of the schema (optional)"""

    nested_properties: NestedProperties
    hash_key: str

    type_format: Optional[str] = None
    """Format (e.g. datetime, uuid) as an extension of the data type"""

    maximum: Optional[float] = None
    """Maximum value for number type if applicable"""

    array_item: Optional["SchemaWrapper"] = None
    all_of: List["SchemaWrapper"] = field(default_factory=list)
    any_of: List["SchemaWrapper"] = field(default_factory=list)
    one_of: List["SchemaWrapper"] = field(default_factory=list)

    enum_values: Optional[List[Any]] = None
    examples: List[Any] = field(default_factory=list)

    def __getitem__(self, item: str) -> "Property":
        try:
            return next(prop for prop in self.properties if prop.name == item)
        except StopIteration:
            raise KeyError(f"No property with name {item} in {self.name}")

    def __contains__(self, item: str) -> bool:
        return any(prop.name == item for prop in self.properties)

    def __iter__(self) -> Iterable["str"]:
        return (prop.name for prop in self.properties)

    @property
    def has_properties(self) -> bool:
        return bool(self.properties or self.any_of or self.all_of)

    @property
    def all_properties(self) -> List["Property"]:
        """All properties of root model and any/oneOf schemas in union"""
        return list(self.all_properties_map.values())

    @property
    def all_properties_map(self) -> Dict[str, "Property"]:
        """All properties of root model and any/oneOf schemas in union"""
        props = {p.name: p for p in self.properties}
        for child in self.any_of + self.one_of:
            for prop in child.all_properties:
                props[prop.name] = prop
        return props

    @property
    def is_object(self) -> bool:
        return "object" in self.types

    @property
    def is_list(self) -> bool:
        return "array" in self.types

    @property
    def union_schemas(self) -> List["SchemaWrapper"]:
        return self.any_of + self.one_of

    @property
    def is_union(self) -> bool:
        return not not self.union_schemas or len(self.types) > 1

    @property
    def type_hint(self) -> str:
        return DataType.from_schema(self).type_hint

    @classmethod
    def from_reference_guarded(
        cls,
        schema_ref: Union[osp.Schema, osp.Reference],
        context: "OpenapiContext",
        parent_properties: Optional[Sequence["Property"]] = None,
        level: int = 0,
    ) -> Optional["SchemaWrapper"]:
        if level >= MAX_RECURSION_DEPTH:
            return None
        level += 1
        return cls.from_reference(schema_ref, context, level=level)

    @classmethod
    def from_reference(
        cls,
        schema_ref: Union[osp.Schema, osp.Reference],
        context: "OpenapiContext",
        level: int = 0,
        parent_properties: Optional[Sequence["Property"]] = None,
    ) -> "SchemaWrapper":
        """Create a Schema wrapper from openapi Schema or reference.
        Recursively generates properties and nested allOf/anyOf/oneOf schemas up to max nesting level

        Args:
            schema_ref: The openapi schema or reference (`$ref`) object pointing to a schema
            context: The parser context
            level: Current recursion level. Used to prevent infinite recursion cycles.
        """
        name, schema = context.schema_and_name_from_reference(schema_ref)

        all_of = _remove_nones([cls.from_reference_guarded(ref, context, level=level) for ref in schema.allOf or []])

        if not name:
            for sub in all_of:
                if name := sub.name:
                    break

        # Properties from all_of child schemas should be merged
        property_map = {prop.name: prop for prop in parent_properties or []}
        property_map.update({prop.name: prop for prop in chain.from_iterable(s.properties for s in all_of)})
        required_props = set(schema.required or [])

        _props_list = _remove_nones(
            [
                Property.from_reference_guarded(name, ref, name in required_props, context, level=level)
                for name, ref in (schema.properties or {}).items()
            ]
        )

        property_map.update({prop.name: prop for prop in _props_list})

        properties = list(property_map.values())

        one_of = _remove_nones(
            [
                cls.from_reference_guarded(ref, context, parent_properties=properties, level=level)
                for ref in schema.oneOf or []
            ]
        )

        any_of = _remove_nones(
            [
                cls.from_reference_guarded(ref, context, parent_properties=properties, level=level)
                for ref in schema.anyOf or []
            ]
        )

        array_item: Optional["SchemaWrapper"] = None
        if schema.items:
            array_item = cls.from_reference_guarded(schema.items, context, level=level)

        # Single type in OAI 3.0, list of types in 3.1
        # Nullable does not exist in 3.1, instead types: ["string", "null"]
        nullable = False
        schema_types = []
        if schema.type:
            schema_types = [schema.type] if not isinstance(schema.type, list) else schema.type.copy()

        for obj in all_of + one_of + any_of:
            schema_types.extend(obj.types)
            if obj.nullable:
                nullable = True

        if "null" in schema_types:
            nullable = True
            schema_types.remove("null")
        wrapper = cls(
            osp_schema=schema,
            name=name,
            description=schema_ref.description or schema.description,
            ref=schema_ref if isinstance(schema_ref, osp.Reference) else None,
            properties=properties,
            all_of=all_of,
            one_of=one_of,
            any_of=any_of,
            types=cast(List[TSchemaType], unique_list(schema_types)),
            nullable=nullable,
            array_item=array_item,
            default=schema.default,
            nested_properties=NestedProperties(),
            hash_key=digest128(schema.json(sort_keys=True)),
            type_format=schema.schema_format,
            maximum=schema.maximum,
            enum_values=schema.enum,
            examples=([schema.example] if schema.example else schema.examples) or [],
        )
        wrapper.nested_properties.discover_nested_properties(wrapper)
        return wrapper


@dataclass
class Property:
    name: str
    required: bool
    schema: SchemaWrapper

    @property
    def is_list(self) -> bool:
        return self.schema.is_list

    @property
    def is_object(self) -> bool:
        return self.schema.is_object

    @property
    def type_hint(self) -> str:
        return DataType.from_property(self).type_hint

    @classmethod
    def from_reference_guarded(
        cls,
        name: str,
        schema_ref: Union[osp.Schema, osp.Reference],
        required: bool,
        context: "OpenapiContext",
        level: int = 0,
    ) -> "Property":
        if level >= MAX_RECURSION_DEPTH:
            return None
        schema = SchemaWrapper.from_reference_guarded(schema_ref, context, level=level)
        return cls(name=name, required=required, schema=schema)


T = TypeVar("T", bound=Any)


def _remove_nones(seq: Iterable[Optional[T]]) -> List[T]:
    return [x for x in seq if x is not None]


class NestedProperties:
    """Creates flattened path: schema mappings of all properties within a schema"""

    def __init__(self) -> None:
        self.object_properties: Dict[Tuple[str, ...], SchemaWrapper] = {}
        self.list_properties: Dict[Tuple[str, ...], SchemaWrapper] = {}
        self.all_properties: Dict[Tuple[str, ...], SchemaWrapper] = {}
        self.required_properties: List[Tuple[str, ...]] = []  # Paths of required properties

    def __getitem__(self, item: Tuple[str, ...]) -> SchemaWrapper:
        return self.all_properties[item]

    def __contains__(self, item: Tuple[str, ...]) -> bool:
        return item in self.all_properties

    def __iter__(self) -> Iterable[Tuple[str, ...]]:
        return iter(self.all_properties.keys())

    def __len__(self) -> int:
        return len(self.all_properties)

    def __bool__(self) -> bool:
        return bool(self.all_properties)

    def items(self) -> Iterable[Tuple[Tuple[str, ...], SchemaWrapper]]:
        return self.all_properties.items()

    def is_optional(self, path: Tuple[str, ...]) -> bool:
        """Check whether the property itself or any of its parents is nullable"""
        check_path = list(path)
        while check_path:
            prop_schema = self.all_properties.get(tuple(check_path))
            # The property is either listed in required properties in openapi, or the property accepts null as a value
            if prop_schema and (tuple(check_path) not in self.required_properties or prop_schema.nullable):
                return True
            check_path.pop()
        return False

    def find_property(
        self, pattern: re.Pattern[str], require_type: Optional[TOpenApiType] = None, allow_unknown_types: bool = True
    ) -> Optional[DataPropertyPath]:
        candidates = []
        unknown_type_candidates = []
        for path, schema in self.items():
            if not path or not pattern.match(path[-1]):
                continue
            if require_type:
                if require_type in schema.types:
                    candidates.append((path, schema))
                elif not schema.types and allow_unknown_types:
                    unknown_type_candidates.append((path, schema))
            else:
                candidates.append((path, schema))

        # prefer least nested path
        candidates.sort(key=lambda item: len(item[0]))
        unknown_type_candidates.sort(key=lambda item: len(item[0]))

        if candidates:
            return DataPropertyPath(*candidates[0])
        elif unknown_type_candidates:
            return DataPropertyPath(*unknown_type_candidates[0])
        return None

    def discover_nested_properties(self, schema: SchemaWrapper, path: Tuple[str, ...] = ()) -> None:
        """Traverse into full property tree and build a map of path to prop for better detection later"""
        self.all_properties[path] = schema
        if schema.is_object:
            self.object_properties[path] = schema
            for prop in schema.all_properties:
                prop_path = path + (prop.name,)
                self.all_properties[prop_path] = prop.schema
                if prop.required:
                    self.required_properties.append(prop_path)
                if prop.is_list or prop.is_object:
                    self.discover_nested_properties(prop.schema, prop_path)
        elif schema.is_list and schema.array_item is not None:
            array_item = schema.array_item
            self.list_properties[path] = array_item
            self.discover_nested_properties(array_item, path + ("[*]",))
