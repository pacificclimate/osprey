from pkg_resources import resource_filename
import os
import pytest
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process, local_path, url_path
from osprey.processes.wps_parameters import Parameters
from .utils import process_err_test


def build_params(
    case_id, grid_id, pour_points, uh_box, routing, domain, config_file, config_dict
):
    return (
        f"case_id={case_id};"
        f"grid_id={grid_id};"
        f"pour_points=@xlink:href={pour_points};"
        f"uh_box=@xlink:href={uh_box};"
        f"routing=@xlink:href={routing};"
        f"domain=@xlink:href={domain};"
        f"config_file=@xlink:href={config_file};"
        f"config_dict=@xlink:href={config_dict};"
    )


@pytest.mark.parametrize(
    (
        "case_id",
        "grid_id",
        "pour_points",
        "uh_box",
        "routing",
        "domain",
        "config_file",
        "config_dict",
    ),
    [
        (
            "sample",
            "COLUMBIA",
            local_path("samples/sample_pour.txt"),
            local_path("samples/uhbox.csv"),
            local_path("samples/sample_flow_parameters.nc"),
            local_path("samples/sample_routing_domain.nc"),
            None,
            None,
        ),
        (
            "sample",
            "COLUMBIA",
            local_path("samples/sample_pour.txt"),
            local_path("samples/uhbox.csv"),
            local_path("samples/sample_flow_parameters.nc"),
            local_path("samples/sample_routing_domain.nc"),
            local_path("configs/parameters.cfg"),
            None,
        ),
        (
            "sample",
            "COLUMBIA",
            local_path("samples/sample_pour.txt"),
            local_path("samples/uhbox.csv"),
            local_path("samples/sample_flow_parameters.nc"),
            local_path("samples/sample_routing_domain.nc"),
            None,
            {"OPTIONS": {"LOG_LEVEL": "CRITICAL",},},
        ),
    ],
)
def test_parameters_local(
    case_id, grid_id, pour_points, uh_box, routing, domain, config_file, config_dict
):
    params = build_params(
        case_id, grid_id, pour_points, uh_box, routing, domain, config_file, config_dict
    )
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
        "config_file",
        "config_dict",
    ),
    [
        (
            "sample",
            "COLUMBIA",
            url_path("sample_pour.txt", "http", "climate_explorer_data_prep"),
            local_path("samples/uhbox.csv"),
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
            local_path("samples/uhbox.csv"),
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
            local_path("samples/uhbox.csv"),
            url_path(
                "sample_flow_parameters.nc", "opendap", "climate_explorer_data_prep"
            ),
            url_path("sample_routing_domain.nc", "http", "climate_explorer_data_prep"),
            None,
            {"OPTIONS": {"LOG_LEVEL": "CRITICAL",},},
        ),
    ],
)
def test_parameters_https(
    case_id, grid_id, pour_points, uh_box, routing, domain, config_file, config_dict
):
    params = build_params(
        case_id, grid_id, pour_points, uh_box, routing, domain, config_file, config_dict
    )
    run_wps_process(Parameters(), params)


@pytest.mark.parametrize(
    (
        "case_id",
        "grid_id",
        "uh_box",
        "routing",
        "domain",
        "config_file",
        "config_dict",
    ),
    [
        (
            "sample",
            "COLUMBIA",
            local_path("samples/uhbox.csv"),
            local_path("samples/sample_flow_parameters.nc"),
            local_path("samples/sample_routing_domain.nc"),
            None,
            None,
        ),
    ],
)
def test_parameters_err(
    case_id, grid_id, uh_box, routing, domain, config_file, config_dict
):
    # Invalid pour_points in empty text file
    with NamedTemporaryFile(
        suffix=".txt", prefix="tmp_copy", dir="/tmp", delete=True
    ) as pour_file:
        params = build_params(
            case_id,
            grid_id,
            pour_file.name,
            uh_box,
            routing,
            domain,
            config_file,
            config_dict,
        )
        process_err_test(Parameters(), params)
