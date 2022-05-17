from pkg_resources import resource_filename
import os
import pytest
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process, local_path, url_path
from osprey.processes.wps_parameters import Parameters
from .utils import process_err_test


@pytest.mark.parametrize(
    (
        "case_id",
        "grid_id",
        "pour_points",
        "uh_box",
        "routing",
        "domain",
        "convolve_config_file",
        "convolve_config_dict",
    ),
    [
        (
            "sample",
            "COLUMBIA",
            resource_filename("tests", "data/samples/sample_pour.txt"),
            resource_filename("tests", "data/samples/uhbox.csv"),
            local_path("samples/sample_flow_parameters.nc"),
            local_path("samples/sample_routing_domain.nc"),
            None,
            None,
        ),
        (
            "sample",
            "COLUMBIA",
            resource_filename("tests", "data/samples/sample_pour.txt"),
            resource_filename("tests", "data/samples/uhbox.csv"),
            local_path("samples/sample_flow_parameters.nc"),
            local_path("samples/sample_routing_domain.nc"),
            local_path("configs/parameters.cfg"),
            None,
        ),
        (
            "sample",
            "COLUMBIA",
            resource_filename("tests", "data/samples/sample_pour.txt"),
            resource_filename("tests", "data/samples/uhbox.csv"),
            local_path("samples/sample_flow_parameters.nc"),
            local_path("samples/sample_routing_domain.nc"),
            None,
            {
                "OPTIONS": {
                    "LOG_LEVEL": "CRITICAL",
                },
            },
        ),
    ],
)
def test_parameters_local(
    case_id,
    grid_id,
    pour_points,
    uh_box,
    routing,
    domain,
    convolve_config_file,
    convolve_config_dict,
):
    with open(uh_box, "r") as uh_box_csv, open(pour_points, "r") as pour_points_csv:
        params = (
            f"case_id={case_id};"
            f"grid_id={grid_id};"
            f"pour_points_csv={pour_points_csv.read()};"
            f"uh_box_csv={uh_box_csv.read()};"
            f"routing=@xlink:href={routing};"
            f"domain=@xlink:href={domain};"
        )

        if convolve_config_file:
            params += f"convolve_config_file=@xlink:href={convolve_config_file};"
        if convolve_config_dict:
            params += f"convolve_config_dict=@xlink:href={convolve_config_dict};"

        run_wps_process(Parameters(), params)


@pytest.mark.online
@pytest.mark.parametrize(
    (
        "case_id",
        "grid_id",
        "pour_points",
        "uh_box",
        "routing",
        "domain",
        "convolve_config_file",
        "convolve_config_dict",
    ),
    [
        (
            "sample",
            "COLUMBIA",
            url_path("sample_pour.txt", "http", "climate_explorer_data_prep"),
            resource_filename("tests", "data/samples/uhbox.csv"),
            url_path(
                "sample_flow_parameters.nc", "opendap", "climate_explorer_data_prep"
            ),
            url_path(
                "sample_routing_domain.nc", "opendap", "climate_explorer_data_prep"
            ),
            None,
            None,
        ),
        (
            "sample",
            "COLUMBIA",
            url_path("sample_pour.txt", "http", "climate_explorer_data_prep"),
            resource_filename("tests", "data/samples/uhbox.csv"),
            url_path(
                "sample_flow_parameters.nc", "opendap", "climate_explorer_data_prep"
            ),
            url_path(
                "sample_routing_domain.nc", "opendap", "climate_explorer_data_prep"
            ),
            local_path("configs/parameters.cfg"),
            None,
        ),
        (
            "sample",
            "COLUMBIA",
            url_path("sample_pour.txt", "http", "climate_explorer_data_prep"),
            resource_filename("tests", "data/samples/uhbox.csv"),
            url_path(
                "sample_flow_parameters.nc", "opendap", "climate_explorer_data_prep"
            ),
            url_path("sample_routing_domain.nc", "http", "climate_explorer_data_prep"),
            None,
            {
                "OPTIONS": {
                    "LOG_LEVEL": "CRITICAL",
                },
            },
        ),
    ],
)
def test_parameters_https(
    case_id,
    grid_id,
    pour_points,
    uh_box,
    routing,
    domain,
    convolve_config_file,
    convolve_config_dict,
):
    with open(uh_box, "r") as uh_box_csv:
        params = (
            f"case_id={case_id};"
            f"grid_id={grid_id};"
            f"pour_points_csv=@xlink:href={pour_points};"
            f"uh_box_csv={uh_box_csv.read()};"
            f"routing=@xlink:href={routing};"
            f"domain=@xlink:href={domain};"
        )

        if convolve_config_file:
            params += f"convolve_config_file=@xlink:href={convolve_config_file};"
        if convolve_config_dict:
            params += f"convolve_config_dict=@xlink:href={convolve_config_dict};"

        run_wps_process(Parameters(), params)


@pytest.mark.parametrize(
    (
        "case_id",
        "grid_id",
        "uh_box",
        "routing",
        "domain",
        "convolve_config_file",
        "convolve_config_dict",
    ),
    [
        (
            "sample",
            "COLUMBIA",
            resource_filename("tests", "data/samples/uhbox.csv"),
            local_path("samples/sample_flow_parameters.nc"),
            local_path("samples/sample_routing_domain.nc"),
            None,
            None,
        ),
    ],
)
def test_parameters_file_err(
    case_id,
    grid_id,
    uh_box,
    routing,
    domain,
    convolve_config_file,
    convolve_config_dict,
):
    # Invalid pour_points in empty text file
    with NamedTemporaryFile(
        suffix=".txt", prefix="tmp_copy", dir="/tmp", delete=True
    ) as pour_file, open(uh_box, "r") as uh_box_csv:
        pour_points_csv = f"file://{pour_file.name}"
        params = (
            f"case_id={case_id};"
            f"grid_id={grid_id};"
            f"pour_points_csv=@xlink:href={pour_points_csv};"
            f"uh_box_csv={uh_box_csv.read()};"
            f"routing=@xlink:href={routing};"
            f"domain=@xlink:href={domain};"
        )
        assert process_err_test(Parameters(), params)
