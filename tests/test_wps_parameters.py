from pkg_resources import resource_filename
import os
import pytest
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process
from osprey.processes.wps_parameters import Parameters
from osprey.utils import replace_filenames


@pytest.mark.parametrize(
    ("config"),
    [
        resource_filename(__name__, "data/configs/parameters_local.cfg"),
        {
            "OPTIONS": {"CASEID": "sample", "GRIDID": "COLUMBIA",},
            "POUR_POINTS": {
                "FILE_NAME": resource_filename(__name__, "data/samples/sample_pour.txt")
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
    ],
)
def test_parameters_local(config):
    params = ("params_config={0};").format(config)
    run_wps_process(Parameters(), params)


@pytest.mark.online
@pytest.mark.parametrize(
    ("config"), [resource_filename(__name__, "data/configs/parameters_https.cfg")],
)
def test_parameters_https(config, conftest_make_mock_urls):
    params = ("params_config={0};").format(config)
    run_wps_process(Parameters(), params)
