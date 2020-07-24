from pkg_resources import resource_filename
import pytest

from wps_tools.testing import run_wps_process, local_path
from osprey.processes.wps_parameters import Parameters


@pytest.mark.parametrize(("config"), [local_path("sample_parameter_config.cfg")])
def test_parameters_local(config):
    params = f"config={config};"
    run_wps_process(Parameters(), params)
