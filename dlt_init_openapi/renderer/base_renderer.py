"""
Basic detector class
"""

from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dlt_init_openapi.parser.openapi_parser import OpenapiParser


class BaseRenderer:
    @abstractmethod
    def run(self, open_api: "OpenapiParser", dry: bool = False) -> None:
        """Run the detector

        Args:
            open_api (OpenapiParser): OpenAPI parser instance

        Raises:
            FileNotFoundError: when specification or other files missing
        """
        ...
