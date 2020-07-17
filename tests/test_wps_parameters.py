from pkg_resources import resource_filename, resource_listdir
import pytest
import re

from pywps import Service
from pywps.tests import assert_response_success

from .common import run_wps_process, local_path, opendap_path
from osprey.processes.wps_parameters import Parameters

test_flow_parameters = (
    "file:///{resource_filename(__name__, 'data/sample_flow_parameters.nc)}"
)
test_pour = "file:///{resource_filename(__name__, 'data/sample_pour.txt)}"
test_routing_domain = (
    "file:///{resource_filename(__name__, 'data/sample_routing_domain.nc)}"
)
test_uhbox = "file:///{resource_filename(__name__, 'data/uhbox.csv)}"
test_config = "file:///{resource_filename(__name__, 'data/sample_parameter_config.cfg)}"


def test_config_file_local():
    params = f"config={test_config};"
    run_wps_process(Parameters(), params)

@pytest.mark.parametrize(("CASEID"), [('sample')])
@pytest.mark.parametrize(("CASE_DIR"), [(resource_listdir(__name__, CASEID))])
@pytest.mark.parametrize(("TEMP_DIR"), [(resource_listdir(__name__, CASEDIR + '/temp/'))])
def test_config_dict_local(CASEID, CASE_DIR, TEMP_DIR):
    config_dict = "{"
                  "LOG_LEVEL: 'INFO',"
                  "VERBOSE: True,"
                  "CLEAN: True,"
                  f"CASEID: {CASEID},"
                  "GRIDID: 'COLUMBIA',"
                  f"CASE_DIR: {CASE_DIR},"
                  f"TEMP_DIR: {TEMP_DIR},"
                  "AGGREGATE False,"
                  "AGG_PAD: 25,"
                  "NETCDF_FORMAT: 'NETCDF4',"
                  "NETCDF_ZLIB: False,"
                  "NETCDF_COMPLEVEL: 4,"
                  "NETCDF_SIGFIGS: None,"
                  "SUBSET_DAYS: 10,"
                  "CONSTRAIN_FRACTIONS: False,"
                  "SEARCH_FOR_CHANNEL: False,"
                  f"FILE_NAME: {test_pour},"
                  f"FILE_NAME: {test_uhbox},"
                  "HEADER_LINES: 1,"
                  f"FILE_NAME: {test_flow_parameters},"
                  "LONGITUDE_VAR: 'lon',"
                  "LATITUDE_VAR: 'lat',"
                  "FLOW_DISTANCE_VAR: 'Flow_Distance',"
                  "FLOW_DIRECTION_VAR: 'Flow_Direction',"
                  "BASIN_ID_VAR: 'Basin_ID',"
                  "VELOCITY: 'velocity',"
                  "DIFFUSION: 'diffusion',"
                  "OUTPUT_INTERVAL: 86400,"
                  "BASIN_FLOWDAYS: 100,"
                  "CELL_FLOWDAYS: 4,"
                  f"FILE_NAME: {test_routing_domain},"
                  "LONGITUDE_VAR: 'lon',"
                  "LATITUDE_VAR: 'lat',"
                  "LAND_MASK_VAR: 'mask',"
                  "FRACTION_VAR: 'frac',"
                  "AREA_VAR: 'area',"
                  "}"
    params = f"config={config_dict};"
    run_wps_process(Parameters(), params)
