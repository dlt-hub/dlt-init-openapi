from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Union

if TYPE_CHECKING:
    from openapi_python_client.parser.endpoints import Parameter


@dataclass
class Pagination:
    pagination_params: List["Parameter"] = field(default_factory=list)
    paginator_config: Dict[str, Union[str, int]] = None

    @property
    def param_names(self) -> List[str]:
        """All params used for pagination"""
        return [param.name for param in self.pagination_params]
