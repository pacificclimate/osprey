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
            resource_filename(__name__, "data/samples/sample_parameter_config.cfg"),
            resource_filename(__name__, "configs/convolve_opendap.cfg"),
        ),
    ],
)
def test_full_rvic(params_config, convolve_config):
    params = f"params_config={params_config};" f"convolve_config={convolve_config};"
    run_wps_process(FullRVIC(), params)
