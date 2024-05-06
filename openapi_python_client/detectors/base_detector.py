"""
Basic detector class
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openapi_python_client.parser.openapi_parser import OpenapiParser


class BaseDetector(ABC):
    @abstractmethod
    def run(self, open_api: "OpenapiParser") -> FileNotFoundError:
        """Run the detector"""
        ...
