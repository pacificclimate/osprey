from pytest import mark
from pywps import Service
from pywps.tests import client_for, assert_response_success
from pkg_resources import resource_filename

from .common import get_output
from osprey.processes.wps_convolution import Convolution


def run_wps_process(process, params):
    client = client_for(Service(processes=[process]))
    datainputs = params
    resp = client.get(
        service="wps",
        request="Execute",
        version="1.0.0",
        identifier=process.identifier,
        datainputs=datainputs,
    )

    assert_response_success(resp)


@mark.parametrize(
    ("config"),
    [f"file:///{resource_filename(__name__, 'configs/convolve_opendap.cfg')}"],
)
def test_wps_convolution(config):
    params = ("config=@xlink:href={0};").format(config)
    run_wps_process(Convolution(), params)
