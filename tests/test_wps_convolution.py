from pytest import mark
from pkg_resources import resource_filename

from wps_tools.testing import run_wps_process, local_path, url_path
from osprey.processes.wps_convolution import Convolution


@mark.slow
@mark.online
@mark.parametrize(
    (
        "case_id",
        "run_startdate",
        "stop_date",
        "domain",
        "param_file",
        "input_forcings",
        "config_file",
        "config_dict",
    ),
    [
        (
            "sample",
            "2012-12-01-00",
            "2012-12-31",
            url_path(
                "projects/comp_support/climate_explorer_data_prep/hydro/sample_data/set4/sample_routing_domain.nc",
                "opendap",
            ),
            url_path(
                "projects/comp_support/climate_explorer_data_prep/hydro/sample_data/set4/sample.rvic.prm.COLUMBIA.20180516.nc",
                "opendap",
            ),
            url_path(
                "projects/comp_support/climate_explorer_data_prep/hydro/sample_data/set4/columbia_vicset2.nc",
                "opendap",
            ),
            None,
            None,
        ),
        (
            "sample",
            "2012-12-01-00",
            "2012-12-31",
            local_path("samples/sample_routing_domain.nc"),
            url_path(
                "projects/comp_support/climate_explorer_data_prep/hydro/sample_data/set4/sample.rvic.prm.COLUMBIA.20180516.nc",
                "opendap",
            ),
            url_path(
                "projects/comp_support/climate_explorer_data_prep/hydro/sample_data/set4/columbia_vicset2.nc",
                "opendap",
            ),
            local_path("configs/convolve.cfg"),
            None,
        ),
        (
            "sample",
            "2012-12-01-00",
            "2012-12-31",
            url_path(
                "projects/comp_support/climate_explorer_data_prep/hydro/sample_data/set4/sample_routing_domain.nc",
                "opendap",
            ),
            local_path("samples/sample.rvic.prm.COLUMBIA.20180516.nc"),
            url_path(
                "projects/comp_support/climate_explorer_data_prep/hydro/sample_data/set4/columbia_vicset2.nc",
                "opendap",
            ),
            None,
            {"OPTIONS": {"CASESTR": "Historical",},},
        ),
    ],
)
def test_wps_convolution(
    case_id,
    run_startdate,
    stop_date,
    domain,
    param_file,
    input_forcings,
    config_file,
    config_dict,
):
    params = (
        f"case_id={case_id};"
        f"run_startdate={run_startdate};"
        f"stop_date={stop_date};"
        f"domain=@xlink:href={domain};"
        f"param_file=@xlink:href={param_file};"
        f"input_forcings=@xlink:href={input_forcings};"
        f"config_file=@xlink:href={config_file};"
        f"config_dict={config_dict};"
    )
    run_wps_process(Convolution(), params)
