# type: ignore

import json
import os
from pathlib import Path

import pytest
import yaml

from dlt_init_openapi.config import Config


def json_with_tabs(d):
    return json.dumps(d, indent=4).replace("    ", "\t")


@pytest.mark.parametrize(
    "filename,dump",
    [
        ("example.yml", yaml.dump),
        ("example.json", json.dumps),
        ("example.yaml", yaml.dump),
        ("example.json", json_with_tabs),
    ],
)
@pytest.mark.parametrize("relative", (True, False), ids=("relative", "absolute"))
def test_load_from_path(tmp_path: Path, filename, dump, relative):
    yml_file = tmp_path.joinpath(filename)
    if relative:
        if not os.getenv("TASKIPY"):
            pytest.skip("Only test relative paths when running with `task check`")
            return
        yml_file = yml_file.relative_to(Path.cwd())
    data = {
        "project_name": "project-name",
        "package_name": "package_name",
    }
    yml_file.write_text(dump(data))

    config = Config.load_from_path(yml_file)
    assert config.project_name == "project_name"
    assert config.package_name == "package_name"


def test_load_from_path_allows_kwargs_to_override_file_values(tmp_path: Path):
    yml_file = tmp_path.joinpath("example.yml")
    yml_file.write_text(
        yaml.dump(
            {
                "project_name": "config-project",
                "package_name": "config_package",
            }
        )
    )

    config = Config.load_from_path(yml_file, project_name="cli-project")

    assert config.project_name == "cli_project"
    assert config.package_name == "config_package"


def test_load_config_keeps_file_project_name_when_source_is_missing(tmp_path: Path):
    from dlt_init_openapi.cli import _load_config

    yml_file = tmp_path.joinpath("config.yml")
    yml_file.write_text(
        yaml.dump(
            {
                "project_name": "posthog",
                "project_folder_suffix": "test",
            }
        )
    )

    config = _load_config(
        path=yml_file,
        config={
            "project_name": None,
            "package_name": None,
            "spec_url": "https://example.com/openapi.yaml",
            "spec_path": None,
            "global_limit": 0,
        },
    )

    assert config.project_name == "posthog"
    assert config.spec_url == "https://example.com/openapi.yaml"
    assert config.project_dir.name == "posthogtest"


def test_ensure_project_dir_rejects_missing_project_name():
    import typer

    from dlt_init_openapi.cli import _ensure_project_dir

    with pytest.raises(typer.BadParameter, match="Provide a source name"):
        _ensure_project_dir(Config(spec_url="https://example.com/openapi.yaml"))
