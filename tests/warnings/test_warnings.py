from dlt_openapi.detector.base_detector import GLOBAL_WARNING_KEY
from dlt_openapi.detector.default.warnings import PrimaryKeyNotFoundWarning, UnresolvedPathParametersWarning
from tests.cases import case_path
from tests.integration.utils import get_detected_project_from_open_api


def test_warnings() -> None:
    path = case_path("artificial", "warnings.yml")
    project = get_detected_project_from_open_api(path, name_resources_by_operation=True)

    # check if the warnings exist that we expect
    warnings = project.detector.get_warnings()

    # no global warnings
    assert not warnings.get(GLOBAL_WARNING_KEY)

    # endpoint ok
    assert not warnings.get("endpoint_ok")

    # missing primary key
    assert len(warnings.get("endpoint_no_primary_key")) == 1
    assert type(warnings.get("endpoint_no_primary_key")[0]) == PrimaryKeyNotFoundWarning

    # path params
    assert len(warnings.get("endpoints_unresolved_path_params")) == 1
    assert type(warnings.get("endpoints_unresolved_path_params")[0]) == UnresolvedPathParametersWarning
    assert warnings.get("endpoints_unresolved_path_params")[0].params == ["hello", "dave"]  # type: ignore
