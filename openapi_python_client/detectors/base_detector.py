"""
Basic detector class
"""

from abc import ABC, abstractmethod


class BaseDetector(ABC):
    @abstractmethod
    def detect_pagination(self) -> None:
        ...

    @abstractmethod
    def detect_payload_path(self) -> None:
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
