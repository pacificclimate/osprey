from pytest import mark
from pkg_resources import resource_filename

from wps_tools.testing import run_wps_process, local_path, url_path
from osprey.processes.wps_full_rvic import FullRVIC
from .utils import process_err_test


@mark.slow
@mark.online
@mark.parametrize(
    (
        "case_id",
        "grid_id",
        "run_startdate",
        "stop_date",
        "pour_points",
        "uh_box",
        "routing",
        "domain",
        "input_forcings",
        "params_config_file",
        "convolve_config_file",
        "params_config_dict",
        "convolve_config_dict",
    ),
    [
        (
            "sample",
            "COLUMBIA",
            "2012-12-01-00",
            "2012-12-31",
            resource_filename("tests", "data/samples/sample_pour.txt"),
            resource_filename("tests", "data/samples/uhbox.csv"),
            local_path("samples/sample_flow_parameters.nc"),
            local_path("samples/sample_routing_domain.nc"),
            url_path("columbia_vicset2.nc", "opendap", "climate_explorer_data_prep"),
            None,
            None,
            {},
            {},
        ),
    ],
)
def test_full_rvic_local_pour_points(
    case_id,
    grid_id,
    run_startdate,
    stop_date,
    pour_points,
    uh_box,
    routing,
    domain,
    input_forcings,
    params_config_file,
    convolve_config_file,
    params_config_dict,
    convolve_config_dict,
):
    with open(uh_box, "r") as uh_box_csv, open(pour_points, "r") as pour_points_csv:
        params = (
            f"case_id={case_id};"
            f"grid_id={grid_id};"
            f"run_startdate={run_startdate};"
            f"stop_date={stop_date};"
            f"pour_points_csv={pour_points_csv.read()};"
            f"uh_box_csv={uh_box_csv.read()};"
            f"routing=@xlink:href={routing};"
            f"domain=@xlink:href={domain};"
            f"input_forcings=@xlink:href={input_forcings};"
            f"params_config_file=@xlink:href={params_config_file};"
            f"convolve_config_file=@xlink:href={convolve_config_file};"
            f"params_config_dict={params_config_dict};"
            f"convolve_config_dict={convolve_config_dict};"
        )
        run_wps_process(FullRVIC(), params)


@mark.slow
@mark.online
@mark.parametrize(
    (
        "case_id",
        "grid_id",
        "run_startdate",
        "stop_date",
        "pour_points",
        "uh_box",
        "routing",
        "domain",
        "input_forcings",
        "params_config_file",
        "convolve_config_file",
        "params_config_dict",
        "convolve_config_dict",
    ),
    [
        (
            "sample",
            "COLUMBIA",
            "2012-12-01-00",
            "2012-12-31",
            url_path("sample_pour.txt", "http", "climate_explorer_data_prep"),
            resource_filename("tests", "data/samples/uhbox.csv"),
            url_path(
                "sample_flow_parameters.nc", "opendap", "climate_explorer_data_prep"
            ),
            local_path("samples/sample_routing_domain.nc"),
            url_path("columbia_vicset2.nc", "opendap", "climate_explorer_data_prep"),
            local_path("configs/parameters.cfg"),
            local_path("configs/convolve.cfg"),
            {},
            {},
        ),
        (
            "sample",
            "COLUMBIA",
            "2012-12-01-00",
            "2012-12-31",
            url_path("sample_pour.txt", "http", "climate_explorer_data_prep"),
            resource_filename("tests", "data/samples/uhbox.csv"),
            url_path(
                "sample_flow_parameters.nc", "opendap", "climate_explorer_data_prep"
            ),
            url_path(
                "sample_routing_domain.nc", "opendap", "climate_explorer_data_prep"
            ),
            url_path("columbia_vicset2.nc", "opendap", "climate_explorer_data_prep"),
            None,
            None,
            {
                "OPTIONS": {
                    "LOG_LEVEL": "CRITICAL",
                },
            },
            {
                "OPTIONS": {
                    "CASESTR": "Historical",
                },
            },
        ),
    ],
)
def test_full_rvic_online_pour_points(
    case_id,
    grid_id,
    run_startdate,
    stop_date,
    pour_points,
    uh_box,
    routing,
    domain,
    input_forcings,
    params_config_file,
    convolve_config_file,
    params_config_dict,
    convolve_config_dict,
):
    with open(uh_box, "r") as uh_box_csv:
        params = (
            f"case_id={case_id};"
            f"grid_id={grid_id};"
            f"run_startdate={run_startdate};"
            f"stop_date={stop_date};"
            f"pour_points_csv=@xlink:href={pour_points};"
            f"uh_box_csv={uh_box_csv.read()};"
            f"routing=@xlink:href={routing};"
            f"domain=@xlink:href={domain};"
            f"input_forcings=@xlink:href={input_forcings};"
            f"params_config_file=@xlink:href={params_config_file};"
            f"convolve_config_file=@xlink:href={convolve_config_file};"
            f"params_config_dict={params_config_dict};"
            f"convolve_config_dict={convolve_config_dict};"
        )
        run_wps_process(FullRVIC(), params)


@mark.slow
@mark.online
@mark.parametrize(
    (
        "case_id",
        "grid_id",
        "run_startdate",
        "stop_date",
        "pour_points",
        "uh_box",
        "routing",
        "domain",
        "input_forcings",
        "params_config_file",
        "convolve_config_file",
        "params_config_dict",
        "convolve_config_dict",
    ),
    [
        (
            "sample",
            "COLUMBIA",
            None,
            "2012-12-31",
            resource_filename("tests", "data/samples/sample_pour.txt"),
            resource_filename("tests", "data/samples/uhbox.csv"),
            local_path("samples/sample_flow_parameters.nc"),
            local_path("samples/sample_routing_domain.nc"),
            url_path("columbia_vicset2.nc", "opendap", "climate_explorer_data_prep"),
            None,
            None,
            {},
            {},
        ),
    ],
)
def test_full_rvic_date_err(
    case_id,
    grid_id,
    run_startdate,
    stop_date,
    pour_points,
    uh_box,
    routing,
    domain,
    input_forcings,
    params_config_file,
    convolve_config_file,
    params_config_dict,
    convolve_config_dict,
):
    with open(uh_box, "r") as uh_box_csv, open(pour_points, "r") as pour_points_csv:
        params = (
            f"case_id={case_id};"
            f"grid_id={grid_id};"
            f"run_startdate={run_startdate};"
            f"stop_date={stop_date};"
            f"pour_points_csv={pour_points_csv.read()};"
            f"uh_box_csv={uh_box_csv.read()};"
            f"routing=@xlink:href={routing};"
            f"domain=@xlink:href={domain};"
            f"input_forcings=@xlink:href={input_forcings};"
            f"params_config_file=@xlink:href={params_config_file};"
            f"convolve_config_file=@xlink:href={convolve_config_file};"
            f"params_config_dict={params_config_dict};"
            f"convolve_config_dict={convolve_config_dict};"
        )
        assert process_err_test(FullRVIC(), params)
