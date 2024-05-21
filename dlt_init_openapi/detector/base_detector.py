"""
Basic detector class
"""

from abc import abstractmethod
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from dlt_init_openapi.parser.openapi_parser import OpenapiParser

GLOBAL_WARNING_KEY = "global"


class BaseDetectionWarning:
    msg: str = ""


class BaseDetector:
    @abstractmethod
    def run(self, open_api: "OpenapiParser") -> None:
        """Run the detector

        Args:
            open_api (OpenapiParser): OpenAPI parser instance
        """
        ...

    @abstractmethod
    def get_warnings(self) -> Dict[str, List[BaseDetectionWarning]]:
        """Get all warnings encountered during detection run"""
        ...
