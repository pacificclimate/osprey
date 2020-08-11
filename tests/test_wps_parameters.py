from pkg_resources import resource_filename
import pytest

from wps_tools.testing import run_wps_process
from osprey.processes.wps_parameters import Parameters


@pytest.mark.parametrize(
    ("config"),
    [resource_filename(__name__, "data/samples/sample_parameter_config.cfg")],
)
def test_parameters_local(config):
    params = f"config={config};"
    run_wps_process(Parameters(), params)
