from pytest import mark
from pywps import Service
from pywps.tests import client_for, assert_response_success
from pkg_resources import resource_filename

from wps_tools.testing import run_wps_process
from osprey.processes.wps_full_rvic import FullRVIC


@mark.slow
@mark.online
@mark.parametrize(
    ("params_config", "convolve_config"),
    [
        (
            resource_filename(__name__, "data/configs/parameters_local.cfg"),
            resource_filename(__name__, "data/configs/convolve_opendap.cfg"),
        ),
        (
            {
                "OPTIONS": {"CASEID": "sample", "GRIDID": "COLUMBIA",},
                "POUR_POINTS": {
                    "FILE_NAME": resource_filename(
                        __name__, "data/samples/sample_pour.txt"
                    )
                },
                "UH_BOX": {
                    "FILE_NAME": resource_filename(__name__, "data/samples/uhbox.csv")
                },
                "ROUTING": {
                    "FILE_NAME": resource_filename(
                        __name__, "data/samples/sample_flow_parameters.nc"
                    )
                },
                "DOMAIN": {
                    "FILE_NAME": resource_filename(
                        __name__, "data/samples/sample_routing_domain.nc"
                    )
                },
            },
            {
                "OPTIONS": {
                    "CASEID": "sample",
                    "RUN_STARTDATE": "2012-12-01-00",
                    "STOP_DATE": "2012-12-31",
                    "CALENDAR": "standard",
                },
                "DOMAIN": {
                    "FILE_NAME": "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/RVIC/sample_routing_domain.nc"
                },
                "INPUT_FORCINGS": {
                    "DATL_PATH": "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/RVIC/",
                    "DATL_FILE": "columbia_vicset2.nc",
                },
            },
        ),
    ],
)
def test_full_rvic(params_config, convolve_config):
    params = f"params_config={params_config};" f"convolve_config={convolve_config};"
    run_wps_process(FullRVIC(), params)
