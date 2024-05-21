from typing import List

from dlt_init_openapi.detector.base_detector import BaseDetectionWarning


class PrimaryKeyNotFoundWarning(BaseDetectionWarning):
    msg: str = "Primary key could not be detected"


class UnresolvedPathParametersWarning(BaseDetectionWarning):

    def __init__(self, params: List[str]) -> None:
        self.params = params
        self.msg = f"Could not resolve all path params, setting default values for: {', '.join(params)}"


class DataResponseUndetectedWarning(BaseDetectionWarning):
    msg: str = (
        "Could not detect the main data response with a status code 2xx. "
        + "Will not be able to detect primary key and some paginators."
    )


class DataResponseNoBodyWarning(BaseDetectionWarning):
    msg: str = (
        "No json response schema defined on main data response. "
        + "Will not be able to detect primary key and some paginators."
    )


class UnsupportedSecuritySchemeWarning(BaseDetectionWarning):
    def __init__(self, security_scheme: str) -> None:
        self.security_scheme = security_scheme
        self.msg = (
            f"Security Scheme {security_scheme} is not supported natively at this time. "
            + "Please provide a custom implementation."
        )


class PossiblePaginatorWarning(BaseDetectionWarning):
    def __init__(self, params: List[str]) -> None:
        self.params = params
        self.msg = (
            "Found params that suggest this endpoint is paginated, but could not discover pagination mechnanism. "
            + f"Params: {', '.join(params)}"
        )
