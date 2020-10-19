from pytest import mark
from pkg_resources import resource_filename

from wps_tools.testing import run_wps_process
from osprey.processes.wps_convert import Convert


@mark.parametrize(
    ("uhs_files", "station_file", "domain", "config_file"),
    [
        (
            f"file:///{resource_filename(__name__, '/data/samples/sample.uh_s2')}",
            f"file:///{resource_filename(__name__, '/data/samples/station_file.txt')}",
            f"file:///{resource_filename(__name__, '/data/samples/sample_routing_domain.nc')}",
            f"file:///{resource_filename(__name__, 'data/configs/convert.cfg')}",
        )
    ],
)
def test_wps_convolution_local(uhs_files, station_file, domain, config_file):
    params = (
        f"uhs_files=@xlink:href={uhs_files};"
        f"station_file=@xlink:href={station_file};"
        f"domain=@xlink:href={domain};"
        f"config_file=@xlink:href={config_file};"
    )
    run_wps_process(Convert(), params)


@mark.online
@mark.parametrize(
    ("uhs_files", "station_file", "domain", "config_file"),
    [
        (
            f"file:///{resource_filename(__name__, '/data/samples/sample.uh_s2')}",
            f"file:///{resource_filename(__name__, '/data/samples/station_file.txt')}",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/fileServer/datasets/RVIC/sample_routing_domain.nc",
            f"file:///{resource_filename(__name__, 'data/configs/convert.cfg')}",
        )
    ],
)
def test_wps_convolution_https(uhs_files, station_file, domain, config_file):
    params = (
        f"uhs_files=@xlink:href={uhs_files};"
        f"station_file=@xlink:href={station_file};"
        f"domain=@xlink:href={domain};"
        f"config_file=@xlink:href={config_file};"
    )
    run_wps_process(Convert(), params)
