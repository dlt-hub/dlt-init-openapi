import pathlib

from loguru import logger


def update_rest_api(force: bool = False) -> None:
    """
    This function is kept for backwards compatibility.
    In dlt >=1.0.0, rest_api is part of the main package.
    No need to vendor the files separately.
    """
    logger.info("Using built-in dlt.sources.rest_api (dlt >=1.11.0)")
    # Create an empty rest_api directory to maintain compatibility
    script_dir = pathlib.Path(__file__).parent.resolve()
    vendor_path = script_dir.parent / "rest_api"
    vendor_path.mkdir(parents=True, exist_ok=True)
    # Create empty __init__.py to make it a proper package
    init_file = vendor_path / "__init__.py"
    if not init_file.exists():
        with open(init_file, "w") as f:
            f.write("# This is a compatibility package. Use dlt.sources.rest_api instead.\n")


if __name__ == "__main__":
    update_rest_api(False)
