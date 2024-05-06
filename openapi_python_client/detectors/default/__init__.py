"""
Default open source detector
"""

from openapi_python_client.detectors.base_detector import BaseDetector


class DefaultDetector(BaseDetector):
    def detect_pagination(self) -> None:
        ...

    def detect_payload_path(self) -> None:
        ...

    def detect_authentication(self) -> None:
        ...

    def detect_primary_key(self) -> None:
        ...

    def detect_parent_endpoint(self) -> None:
        ...
