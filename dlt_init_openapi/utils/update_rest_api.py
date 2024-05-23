import pathlib

import requests
from loguru import logger

from dlt_init_openapi.config import REST_API_SOURCE_LOCATION

BASEPATH = "https://raw.githubusercontent.com/dlt-hub/verified-sources/master/sources/rest_api/"
FILES = ["README.md", "__init__.py", "config_setup.py", "exceptions.py", "requirements.txt", "typing.py", "utils.py"]


def update_rest_api(force: bool = False) -> None:
    """updates local rest api"""
    logger.info("Syncing rest_api verified source")

    path = pathlib.Path(REST_API_SOURCE_LOCATION)
    if path.exists() and not force:
        logger.info("rest_api verified source already present")
        return

    path.mkdir(exist_ok=True)
    for file in FILES:
        src_path = BASEPATH + file
        dst_path = REST_API_SOURCE_LOCATION + "/" + file
        logger.info(f"Copying {src_path}")
        with requests.get(src_path, stream=True) as r:
            r.raise_for_status()
            with open(dst_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    logger.success("rest_api verified source synced")


if __name__ == "__main__":
    update_rest_api(False)
