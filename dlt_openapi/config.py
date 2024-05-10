import json
import mimetypes
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel

from .typing import TEndpointFilter


class Config(BaseModel):
    """Contains any configurable values passed by the user."""

    project_name: Optional[str] = None
    """Custom name for the created project"""
    package_name: Optional[str] = None
    """Custom name for the created package"""
    post_hooks: List[str] = [
        "autoflake -i -r --remove-all-unused-imports --remove-unused-variables .",
        "isort --float-to-top .",
        "black .",
    ]
    """Commands to run after code generation"""
    include_methods: List[str] = ["get"]
    """HTTP methods to render from OpenAPI spec"""
    fallback_openapi_title: str = "openapi"
    """Fallback title when openapi info.title is missing or empty"""
    project_name_suffix: str = "-pipeline"
    """Suffix for project name"""
    dataset_name_suffix: str = "_data"
    """Suffix for dataset"""
    endpoint_filter: Optional[TEndpointFilter] = None
    """filter for endpoint rendering"""
    name_resources_by_operation: bool = False
    """always name resources by operation id, useful for testing"""

    @staticmethod
    def load_from_path(path: Path) -> "Config":
        """Creates a Config from provided JSON or YAML file and sets a bunch of globals from it"""
        mime = mimetypes.guess_type(path.absolute().as_uri(), strict=True)[0]
        if mime == "application/json":
            config_data = json.loads(path.read_text())
        else:
            config_data = yaml.safe_load(path.read_text())
        config = Config(**config_data)
        return config
