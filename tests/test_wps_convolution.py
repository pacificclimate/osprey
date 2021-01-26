from pytest import mark
from pkg_resources import resource_filename
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process, local_path, url_path
from osprey.processes.wps_convolution import Convolution
from .utils import process_err_test


def build_params(
    case_id,
    run_startdate,
    stop_date,
    domain,
    param_file,
    input_forcings,
    config_file,
    config_dict,
):
    return (
        f"case_id={case_id};"
        f"run_startdate={run_startdate};"
        f"stop_date={stop_date};"
        f"domain=@xlink:href={domain};"
        f"param_file=@xlink:href={param_file};"
        f"input_forcings=@xlink:href={input_forcings};"
        f"config_file=@xlink:href={config_file};"
        f"config_dict={config_dict};"
    )


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
                "sample_routing_domain.nc", "opendap", "climate_explorer_data_prep"
            ),
            url_path(
                "sample.rvic.prm.COLUMBIA.20180516.nc",
                "opendap",
                "climate_explorer_data_prep",
            ),
            url_path("columbia_vicset2.nc", "opendap", "climate_explorer_data_prep"),
            None,
            None,
        ),
        (
            "sample",
            "2012-12-01-00",
            "2012-12-31",
            local_path("samples/sample_routing_domain.nc"),
            url_path(
                "sample.rvic.prm.COLUMBIA.20180516.nc",
                "opendap",
                "climate_explorer_data_prep",
            ),
            url_path("columbia_vicset2.nc", "opendap", "climate_explorer_data_prep"),
            local_path("configs/convolve.cfg"),
            None,
        ),
        (
            "sample",
            "2012-12-01-00",
            "2012-12-31",
            url_path(
                "sample_routing_domain.nc", "opendap", "climate_explorer_data_prep"
            ),
            local_path("samples/sample.rvic.prm.COLUMBIA.20180516.nc"),
            url_path("columbia_vicset2.nc", "opendap", "climate_explorer_data_prep"),
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
    params = build_params(
        case_id,
        run_startdate,
        stop_date,
        domain,
        param_file,
        input_forcings,
        config_file,
        config_dict,
    )
    run_wps_process(Convolution(), params)


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
        "config_dict",
    ),
    [
        (
            "sample",
            None,  # Date cannot be None
            "2012-12-31",
            local_path("samples/sample_routing_domain.nc"),
            url_path(
                "sample.rvic.prm.COLUMBIA.20180516.nc",
                "opendap",
                "climate_explorer_data_prep",
            ),
            url_path("columbia_vicset2.nc", "opendap", "climate_explorer_data_prep"),
            None,
        ),
    ],
)
def test_wps_convolution_err(
    case_id, run_startdate, stop_date, domain, param_file, input_forcings, config_dict,
):
    with NamedTemporaryFile(
        suffix=".cfg", prefix="tmp_copy", dir="/tmp", delete=True
    ) as config_file:
        params = build_params(
            case_id,
            run_startdate,
            stop_date,
            domain,
            param_file,
            input_forcings,
            config_file.name,
            config_dict,
        )
    process_err_test(Convolution(), params)
