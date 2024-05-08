"""
Default renderer
"""
import logging
import shutil
import subprocess
from distutils.dir_util import copy_tree
from pathlib import Path

from jinja2 import Environment, PackageLoader

from openapi_python_client.config import Config
from openapi_python_client.parser.openapi_parser import OpenapiParser
from openapi_python_client.renderer.base_renderer import BaseRenderer
from openapi_python_client.utils import misc

log = logging.getLogger(__name__)

REST_API_SOURCE_LOCATION = "./sources/sources/rest_api"
FILE_ENCODING = "utf-8"
TEMPLATE_FILTERS = {
    "snakecase": misc.snake_case,
    "kebabcase": misc.kebab_case,
    "pascalcase": misc.pascal_case,
    "any": any,
}


class DefaultRenderer(BaseRenderer):
    openapi: OpenapiParser

    def __init__(self, config: Config) -> None:
        self.config = config

        self.env: Environment = Environment(
            loader=PackageLoader(__package__),
            trim_blocks=True,
            lstrip_blocks=True,
            extensions=["jinja2.ext.loopcontrols"],
            keep_trailing_newline=True,
        )

        self.env.filters.update(TEMPLATE_FILTERS)

    def run(self, openapi: OpenapiParser, dry: bool = False) -> None:
        """Run the renderer"""
        self.openapi = openapi

        # set up some paths
        project_name_base: str = self.config.project_name_override or f"{misc.kebab_case(openapi.info.title).lower()}"
        self.project_name = project_name_base + self.config.project_name_suffix
        self.package_name = (self.config.package_name_override or self.project_name).replace("-", "_")
        self.source_name = self.package_name + "_source"
        self.dataset_name = self.package_name + self.config.dataset_name_suffix
        self.project_dir = Path.cwd() / self.project_name
        self.package_dir = self.project_dir / self.package_name

        self.env.globals.update(
            utils=misc,
            class_name=lambda x: misc.ClassName(x, ""),
            package_name=self.package_name,
            project_name=self.project_name,
        )

        if dry:
            return

        self._create_package()
        self._build_dlt_config()
        self._build_source()
        self._build_pipeline()
        self._run_post_hooks()

        # copy rest api source into project dir
        copy_tree(REST_API_SOURCE_LOCATION, str(self.project_dir / "rest_api"))

    def _create_package(self) -> None:
        self.project_dir.mkdir(exist_ok=True)
        self.package_dir.mkdir()

    def _build_dlt_config(self) -> None:
        config_dir = self.project_dir / ".dlt"
        config_dir.mkdir()

        servers = self.openapi.info.servers
        first_server = servers[0] if servers else None
        other_servers = servers[1:]
        if first_server and first_server.url == "/" and not first_server.description:
            # Remove default server
            first_server = None

        config_template = self.env.get_template("dlt_config.toml.j2")
        config_path = config_dir / "config.toml"
        config_path.write_text(
            config_template.render(
                first_server=first_server, other_servers=other_servers, source_name=self.source_name
            ),
            encoding=FILE_ENCODING,
        )

    def _build_source(self) -> None:
        module_path = self.package_dir / "__init__.py"
        module_path.write_text(
            self._render_source(),
            encoding=FILE_ENCODING,
        )

    def _render_source(self) -> str:
        template = self.env.get_template("source.py.j2")
        return template.render(
            source_name=self.source_name,
            endpoint_collection=self.openapi.endpoints,
            imports=[],
            credentials=self.openapi.credentials,
        )

    def _build_pipeline(self) -> None:
        module_path = self.project_dir / "pipeline.py"

        template = self.env.get_template("pipeline.py.j2")
        module_path.write_text(
            template.render(
                package_name=self.package_name, source_name=self.source_name, dataset_name=self.dataset_name
            ),
            encoding=FILE_ENCODING,
        )

    def _run_post_hooks(self) -> None:
        for command in self.config.post_hooks:
            self._run_command(command)

    def _run_command(self, cmd: str) -> None:
        cmd_name = cmd.split(" ")[0]
        command_exists = shutil.which(cmd_name)
        if not command_exists:
            log.warning("Skipping integration: %s is not in PATH", cmd_name)
            return
        cwd = self.package_dir
        try:
            subprocess.run(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError as err:
            raise RuntimeError("{}failed\n{}".format(cmd_name, err.stderr.decode() or err.output.decode())) from err
