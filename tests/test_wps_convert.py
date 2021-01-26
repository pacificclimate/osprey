import configparser
from pytest import mark
from pkg_resources import resource_filename
from rvic.core.config import read_config


from wps_tools.testing import run_wps_process, local_path, url_path
from osprey.processes.wps_convert import Convert
from .utils import process_err_test


def build_params(uhs_files, station_file, domain, config_file):
    return (
        f"uhs_files=@xlink:href={uhs_files};"
        f"station_file=@xlink:href={station_file};"
        f"domain=@xlink:href={domain};"
        f"config_file=@xlink:href={config_file};"
    )


@mark.parametrize(
    ("uhs_files", "station_file", "domain", "config_file"),
    [
        (
            local_path("samples/sample.uh_s2"),
            local_path("samples/station_file.txt"),
            local_path("samples/sample_routing_domain.nc"),
            local_path("configs/convert.cfg"),
        )
    ],
)
def test_wps_convert_local(uhs_files, station_file, domain, config_file):
    params = build_params(uhs_files, station_file, domain, config_file)
    run_wps_process(Convert(), params)


@mark.online
@mark.parametrize(
    ("uhs_files", "station_file", "domain", "config_file"),
    [
        (
            local_path("samples/sample.uh_s2"),
            local_path("samples/station_file.txt"),
            url_path("sample_routing_domain.nc", "http", "climate_explorer_data_prep"),
            local_path("configs/convert.cfg"),
        )
    ],
)
def test_wps_convert_https(uhs_files, station_file, domain, config_file):
    params = build_params(uhs_files, station_file, domain, config_file)
    run_wps_process(Convert(), params)


@mark.online
@mark.parametrize(
    ("uhs_files", "station_file", "domain", "config_file"),
    [
        (
            local_path("samples/sample.uh_s2"),
            local_path("samples/station_file.txt"),
            url_path("sample_routing_domain.nc", "http", "climate_explorer_data_prep"),
            # convolve.cfg has wrong keys
            local_path("configs/convolve.cfg"),
        )
    ],
)
def test_wps_convert_config_err(uhs_files, station_file, domain, config_file):
    params = build_params(uhs_files, station_file, domain, config_file)
    assert process_err_test(Convert(), params)


@mark.online
@mark.parametrize(
    ("uhs_files", "station_file", "domain", "config_file"),
    [
        (
            local_path("samples/sample.uh_s2"),
            local_path("samples/station_file.txt"),
            url_path("sample_routing_domain.nc", "http", "climate_explorer_data_prep"),
            # convert[UHS_FILES][ROUT_PROGRAM] is Python (should be C pr Fortran)
            local_path("configs/convert_err.cfg"),
        )
    ],
)
def test_wps_convert_rvic_err(uhs_files, station_file, domain, config_file):
    params = build_params(uhs_files, station_file, domain, config_file)
    assert process_err_test(Convert(), params)
