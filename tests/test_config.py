# type: ignore

import json
import os
from pathlib import Path

import pytest
import yaml

from dlt_openapi.config import Config


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
    assert config.project_name == "project-name"
    assert config.package_name == "package_name"
