from pytest import mark
from pkg_resources import resource_filename

from wps_tools.testing import run_wps_process
from osprey.processes.wps_convert import Convert


@mark.parametrize(
    ("config"), [f"{resource_filename(__name__, 'data/configs/convert_local.cfg')}",],
)
def test_wps_convolution_local(config):
    params = ("convert_config={0};").format(config)
    run_wps_process(Convert(), params)


@mark.online
@mark.parametrize(
    ("config"), [f"{resource_filename(__name__, 'data/configs/convert_mixed.cfg')}",],
)
def test_wps_convolution_https(config):
    params = ("convert_config={0};").format(config)
    run_wps_process(Convert(), params)
