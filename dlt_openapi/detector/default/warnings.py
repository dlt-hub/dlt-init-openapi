from dlt_openapi.detector.base_detector import BaseDetectionWarning


class PrimaryKeyNotFoundWarning(BaseDetectionWarning):
    msg: str = "Primary key could not be detected"
