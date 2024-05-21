from dataclasses import dataclass
from typing import List, Optional

import openapi_schema_pydantic as osp

from dlt_init_openapi.parser.context import OpenapiContext


@dataclass
class OpenApiInfo:
    title: str
    version: str
    summary: Optional[str]
    description: Optional[str]
    servers: List[osp.Server]

    @classmethod
    def from_context(cls, context: OpenapiContext) -> "OpenApiInfo":
        info = context.spec.info
        return cls(
            title=info.title or context.config.fallback_openapi_title,
            summary=info.summary,
            description=info.description,
            version=info.version or "",
            servers=context.spec.servers or [],
        )
