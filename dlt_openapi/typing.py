from typing import TYPE_CHECKING, Callable, Set

if TYPE_CHECKING:
    from dlt_openapi.parser.endpoints import EndpointCollection


TEndpointFilter = Callable[["EndpointCollection"], Set[str]]
