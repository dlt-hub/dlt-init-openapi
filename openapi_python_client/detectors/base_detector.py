"""
Basic detector class
"""
from typing import Tuple, TYPE_CHECKING, Dict, Optional
from abc import ABC, abstractmethod
import openapi_schema_pydantic as osp

if TYPE_CHECKING:
    from openapi_python_client.parser.pagination import Pagination
    from openapi_python_client.parser.endpoints import Response
    from openapi_python_client.parser.context import OpenapiContext
    from openapi_python_client.parser.parameters import Parameter
    from openapi_python_client.parser.models import SchemaWrapper, DataPropertyPath


class BaseDetector(ABC):
    context: "OpenapiContext"

    @abstractmethod
    def detect_response_and_pagination(
        self, path: str, operation: osp.Operation, parameters: Dict[str, "Parameter"]
    ) -> Tuple[Optional["Pagination"], Optional["Response"]]:
        """Get response and pagination from osp.operation"""
        ...

    @abstractmethod
    def detect_payload(self, content_schema: "SchemaWrapper", expect_list: bool) -> Optional["DataPropertyPath"]:
        """Detect json path of the actual payload within a content schema"""
        ...

    @abstractmethod
    def detect_authentication(self) -> None:
        ...

    @abstractmethod
    def detect_primary_key(self) -> None:
        ...

    @abstractmethod
    def detect_parent_endpoint(self) -> None:
        ...

    @abstractmethod
    def detect_transformer_mapping(self) -> None:
        ...
