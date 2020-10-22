from pytest import mark
from pkg_resources import resource_filename

from wps_tools.testing import run_wps_process
from osprey.processes.wps_full_rvic import FullRVIC


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
            f"file:///{resource_filename(__name__, 'data/samples/sample_pour.txt')}",
            f"file:///{resource_filename(__name__, 'data/samples/uhbox.csv')}",
            f"file:///{resource_filename(__name__, 'data/samples/sample_flow_parameters.nc')}",
            f"file:///{resource_filename(__name__, 'data/samples/sample_routing_domain.nc')}",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/RVIC/columbia_vicset2.nc",
            None,
            None,
            {},
            {},
        ),
        (
            "sample",
            "COLUMBIA",
            "2012-12-01-00",
            "2012-12-31",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/fileServer/datasets/RVIC/sample_pour.txt",
            f"file:///{resource_filename(__name__, 'data/samples/uhbox.csv')}",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/fileServer/datasets/RVIC/sample_flow_parameters.nc",
            f"file:///{resource_filename(__name__, 'data/samples/sample_routing_domain.nc')}",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/RVIC/columbia_vicset2.nc",
            f"file:///{resource_filename(__name__, '/data/configs/parameters.cfg')}",
            f"file:///{resource_filename(__name__, '/data/configs/convolve.cfg')}",
            {},
            {},
        ),
        (
            "sample",
            "COLUMBIA",
            "2012-12-01-00",
            "2012-12-31",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/fileServer/datasets/RVIC/sample_pour.txt",
            f"file:///{resource_filename(__name__, 'data/samples/uhbox.csv')}",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/fileServer/datasets/RVIC/sample_flow_parameters.nc",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/fileServer/datasets/RVIC/sample_routing_domain.nc",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/RVIC/columbia_vicset2.nc",
            None,
            None,
            {"OPTIONS": {"LOG_LEVEL": "CRITICAL",},},
            {"OPTIONS": {"CASESTR": "Historical",},},
        ),
    ],
)
def test_full_rvic(
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
    params = (
        f"case_id={case_id};"
        f"grid_id={grid_id};"
        f"run_startdate={run_startdate};"
        f"stop_date={stop_date};"
        f"pour_points=@xlink:href={pour_points};"
        f"uh_box=@xlink:href={uh_box};"
        f"routing=@xlink:href={routing};"
        f"domain=@xlink:href={domain};"
        f"input_forcings=@xlink:href={input_forcings};"
        f"params_config_file=@xlink:href={params_config_file};"
        f"convolve_config_file=@xlink:href={convolve_config_file};"
        f"params_config_dict={params_config_dict};"
        f"convolve_config_dict={convolve_config_dict};"
    )
    run_wps_process(FullRVIC(), params)
