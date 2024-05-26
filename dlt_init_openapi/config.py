import json
import mimetypes
import pathlib
from pathlib import Path
from typing import Any, List, Optional

import yaml
from pydantic import BaseModel

from dlt_init_openapi.utils.misc import snake_case

from .typing import TEndpointFilter

REST_API_SOURCE_LOCATION = str(pathlib.Path(__file__).parent.resolve() / "../rest_api")


class Config(BaseModel):
    """Contains any configurable values passed by the user."""

    output_path: Optional[Path] = None
    """Path for the render output"""
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
    project_folder_suffix: str = "_pipeline"
    """Suffix for project name"""
    pipeline_file_suffix: str = "_pipeline.py"
    """Suffix for pipeline file name"""
    dataset_name_suffix: str = "_data"
    """Suffix for dataset"""
    endpoint_filter: Optional[TEndpointFilter] = None
    """filter for endpoint rendering"""
    name_resources_by_operation: bool = False
    """always name resources by operation id, useful for testing"""
    renderer_class: str = "dlt_init_openapi.renderer.default.DefaultRenderer"
    """Which class to use for rendering"""
    detector_class: str = "dlt_init_openapi.detector.default.DefaultDetector"
    """Which class to use for detecting"""
    global_limit: int = 0
    """Set a limit on how many items are emitted from a resource"""
    required_parameter_default_value: str = "FILL_ME_IN"
    """default to render for required parameters that do not have a default in the spec"""
    unrequired_parameter_default_value: str = "OPTIONAL_CONFIG"
    """default to render for unrequired parameters that do not have a default in the spec"""
    allow_openapi_2: bool = False
    """Allow to use OpenAPI 2 specs"""

    # internal, do not set via config file
    project_dir: Path = None
    pipeline_file_name: str = None
    spec_url: str = None
    spec_path: Path = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(Config, self).__init__(*args, **kwargs)
        self.prepare()

    def prepare(self) -> None:
        # normalize a couple of vars
        self.project_name = snake_case(self.project_name)
        self.package_name = snake_case(self.package_name)

        if self.project_name and self.project_folder_suffix:
            base_dir = Path.cwd() if not self.output_path else Path.cwd() / self.output_path
            project_folder = self.project_name + self.project_folder_suffix
            self.project_dir = base_dir / project_folder
            self.pipeline_file_name = self.project_name + self.pipeline_file_suffix

    @staticmethod
    def load_from_path(path: Path, *args: Any, **kwargs: Any) -> "Config":
        """Creates a Config from provided JSON or YAML file and sets a bunch of globals from it"""
        mime = mimetypes.guess_type(path.absolute().as_uri(), strict=True)[0]
        if mime == "application/json":
            config_data = json.loads(path.read_text())
        else:
            config_data = yaml.safe_load(path.read_text())
        config = Config(**config_data, **kwargs)
        return config
