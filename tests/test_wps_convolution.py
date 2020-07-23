from pytest import mark
from pywps import Service
from pywps.tests import client_for, assert_response_success
from pkg_resources import resource_filename

from .common import run_wps_process
from osprey.processes.wps_convolution import Convolution


@mark.parametrize(
    ("config"),
    [f"file:///{resource_filename(__name__, 'configs/convolve_opendap.cfg')}"],
)
def test_wps_convolution(config):
    params = ("config=@xlink:href={0};").format(config)
    run_wps_process(Convolution(), params)
