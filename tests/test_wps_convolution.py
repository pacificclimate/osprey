from pytest import mark
from pywps import Service
from pywps.tests import client_for, assert_response_success
from pkg_resources import resource_filename

from .common import run_wps_process
from osprey.processes.wps_convolution import Convolution

# ********************************************************************************
#   The test is disabled due to failues caused by RVIC's internal issues:
#   https://github.com/UW-Hydro/RVIC/issues/96
#   https://github.com/UW-Hydro/RVIC/issues/130
# ********************************************************************************
# @mark.slow
# @mark.online
# @mark.parametrize(
#     ("config"),
#     [
#         f"{resource_filename(__name__, 'configs/convolve_opendap.cfg')}",
#         {
#             "OPTIONS": {
#                 "CASEID": "sample",
#                 "RUN_STARTDATE": "2012-12-01-00",
#                 "STOP_DATE": "2012-12-31",
#                 "CALENDAR": "standard",
#             },
#             "DOMAIN": {
#                 "FILE_NAME": "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/RVIC/sample_routing_domain.nc"
#             },
#             "PARAM_FILE": {
#                 "FILE_NAME": "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/RVIC/sample.rvic.prm.COLUMBIA.20180516.nc"
#             },
#             "INPUT_FORCINGS": {
#                 "DATL_PATH": "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/RVIC/",
#                 "DATL_FILE": "columbia_vicset2.nc",
#             },
#         },
#     ],
# )
# def test_wps_convolution(config):
#     params = ("config={0};").format(config)
#     run_wps_process(Convolution(), params)
