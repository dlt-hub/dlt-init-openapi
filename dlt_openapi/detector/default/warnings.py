from typing import List

from dlt_openapi.detector.base_detector import BaseDetectionWarning


class PrimaryKeyNotFoundWarning(BaseDetectionWarning):
    msg: str = "Primary key could not be detected"


class UnresolvedPathParametersWarning(BaseDetectionWarning):

    def __init__(self, params: List[str]) -> None:
        self.params = params
        self.msg = f"Could not resolve all path params, setting default values for: {','.join(params)}"
