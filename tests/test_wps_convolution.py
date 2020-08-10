from pytest import mark
from pywps import Service
from pywps.tests import client_for, assert_response_success
from pkg_resources import resource_filename

from .common import run_wps_process
from osprey.processes.wps_convolution import Convolution

#********************************************************************************
#   The test is disabled due to failues caused by RVIC's internal issues:
#   https://github.com/UW-Hydro/RVIC/issues/96
#   https://github.com/UW-Hydro/RVIC/issues/130
#********************************************************************************
# @mark.slow
# @mark.online
# @mark.parametrize(
#     ("config"), [f"{resource_filename(__name__, 'configs/convolve_opendap.cfg')}"],
# )
# def test_wps_convolution(config):
#     params = ("config={0};").format(config)
#     run_wps_process(Convolution(), params)
