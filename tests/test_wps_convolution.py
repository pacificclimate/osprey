from pytest import mark
from pkg_resources import resource_filename

from wps_tools.testing import run_wps_process
from osprey.processes.wps_convolution import Convolution


@mark.slow
@mark.online
@mark.parametrize(
    ("case_id", "run_startdate", "stop_date", "domain", "param_file", "input_forcings", "config_file", "config_dict"),
    [
        (
            "sample",
            "2012-12-01-00",
            "2012-12-31",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/RVIC/sample_routing_domain.nc",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/RVIC/sample.rvic.prm.COLUMBIA.20180516.nc",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/RVIC/columbia_vicset2.nc",
            None,
            None,
        ),    
        (
            "sample",
            "2012-12-01-00",
            "2012-12-31",
            f"file:///{resource_filename(__name__, 'data/samples/sample_routing_domain.nc')}",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/RVIC/sample.rvic.prm.COLUMBIA.20180516.nc",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/RVIC/columbia_vicset2.nc",
            f"file:///{resource_filename(__name__, '/data/configs/convolve.cfg')}",
            None,
        ),    
        (
            "sample",
            "2012-12-01-00",
            "2012-12-31",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/RVIC/sample_routing_domain.nc",
            f"file:///{resource_filename(__name__, 'data/samples/sample.rvic.prm.COLUMBIA.20180516.nc')}",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/RVIC/columbia_vicset2.nc",
            None,
            {
                "OPTIONS": {
                    "CASESTR": "Historical",
                },
            }
        ),    
    ],
)
def test_wps_convolution(case_id, run_startdate, stop_date, domain, param_file, input_forcings, config_file, config_dict):
    params = (
        f"case_id={case_id};"
        f"run_startdate={run_startdate};"
        f"stop_date={stop_date};"
        f"domain=@xlink:href={domain};"
        f"param_file=@xlink:href={param_file};"
        f"input_forcings=@xlink:href={input_forcings};"
        f"config_file={config_file};"
        f"config_dict={config_dict};"
    )
    run_wps_process(Convolution(), params)
