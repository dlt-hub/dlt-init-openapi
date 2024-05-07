from typing import TYPE_CHECKING, Callable, Set, Tuple

if TYPE_CHECKING:
    from openapi_python_client.parser.endpoints import EndpointCollection


TEndpointFilter = Callable[["EndpointCollection"], Tuple[Set[str], Set[str]]]
