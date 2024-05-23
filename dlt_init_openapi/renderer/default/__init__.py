"""
Default renderer
"""

import shutil
import subprocess
from distutils.dir_util import copy_tree

from jinja2 import Environment, PackageLoader
from loguru import logger

from dlt_init_openapi.config import REST_API_SOURCE_LOCATION, Config
from dlt_init_openapi.parser.openapi_parser import OpenapiParser
from dlt_init_openapi.renderer.base_renderer import BaseRenderer
from dlt_init_openapi.utils import misc

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
        self.package_name = (self.config.package_name or self.config.project_name).replace("-", "_")
        self.source_name = self.package_name + "_source"
        self.dataset_name = self.package_name + self.config.dataset_name_suffix
        self.package_dir = self.config.project_dir / self.package_name

        self.env.globals.update(
            utils=misc,
            class_name=lambda x: misc.ClassName(x, ""),
            package_name=self.package_name,
            project_name=self.config.project_name,
            credentials=self.openapi.detected_global_security_scheme,
            config=self.config,
        )

        if dry:
            return

        self._create_package()
        self._build_dlt_config()
        self._build_source()
        self._build_pipeline()
        self._build_meta_files()
        self._run_post_hooks()

        # copy rest api source into project dir
        copy_tree(REST_API_SOURCE_LOCATION, str(self.config.project_dir / "rest_api"))

    def _build_meta_files(self) -> None:
        requirements_template = self.env.get_template("requirements.txt.j2")
        req_path = self.config.project_dir / "requirements.txt"
        req_path.write_text(
            requirements_template.render(),
            encoding=FILE_ENCODING,
        )

        from dlt_init_openapi import __version__

        readme_template = self.env.get_template("README.md.j2")
        readme_path = self.config.project_dir / "README.md"
        readme_path.write_text(
            readme_template.render(endpoint_collection=self.openapi.endpoints, version=__version__),
            encoding=FILE_ENCODING,
        )

        gitignore_template = self.env.get_template("gitignore.j2")
        gitignore_path = self.config.project_dir / ".gitignore"
        gitignore_path.write_text(
            gitignore_template.render(),
            encoding=FILE_ENCODING,
        )

    def _create_package(self) -> None:
        self.config.project_dir.mkdir(exist_ok=True, parents=True)
        self.package_dir.mkdir(exist_ok=True)

    def _build_dlt_config(self) -> None:
        config_dir = self.config.project_dir / ".dlt"
        config_dir.mkdir(exist_ok=True)

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

        secrets_template = self.env.get_template("dlt_secrets.toml.j2")
        secrets_path = config_dir / "secrets.toml"
        secrets_path.write_text(
            secrets_template.render(),
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
            global_paginator_config=(
                self.openapi.detected_global_pagination.paginator_config
                if self.openapi.detected_global_pagination
                else None
            ),
        )

    def _build_pipeline(self) -> None:
        module_path = self.config.project_dir / self.config.pipeline_file_name

        template = self.env.get_template("pipeline.py.j2")
        module_path.write_text(
            template.render(
                package_name=self.package_name,
                source_name=self.source_name,
                dataset_name=self.dataset_name,
                global_limit=self.config.global_limit,
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
            logger.warning("Skipping integration: %s is not in PATH", cmd_name)
            return
        cwd = self.package_dir
        try:
            subprocess.run(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError as err:
            raise RuntimeError("{}failed\n{}".format(cmd_name, err.stderr.decode() or err.output.decode())) from err
