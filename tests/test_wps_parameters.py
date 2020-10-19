from pkg_resources import resource_filename
import os
import pytest
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process
from osprey.processes.wps_parameters import Parameters


@pytest.mark.parametrize(
    (
        "case_id",
        "grid_id",
        "pour_points",
        "uh_box",
        "routing",
        "domain",
        "config_file",
        "config_dict",
    ),
    [
        (
            "sample",
            "COLUMBIA",
            f"file:///{resource_filename(__name__, 'data/samples/sample_pour.txt')}",
            f"file:///{resource_filename(__name__, 'data/samples/uhbox.csv')}",
            f"file:///{resource_filename(__name__, 'data/samples/sample_flow_parameters.nc')}",
            f"file:///{resource_filename(__name__, 'data/samples/sample_routing_domain.nc')}",
            None,
            None,
        ),
        (
            "sample",
            "COLUMBIA",
            f"file:///{resource_filename(__name__, 'data/samples/sample_pour.txt')}",
            f"file:///{resource_filename(__name__, 'data/samples/uhbox.csv')}",
            f"file:///{resource_filename(__name__, 'data/samples/sample_flow_parameters.nc')}",
            f"file:///{resource_filename(__name__, 'data/samples/sample_routing_domain.nc')}",
            f"file:///{resource_filename(__name__, '/data/configs/parameters.cfg')}",
            None,
        ),
        (
            "sample",
            "COLUMBIA",
            f"file:///{resource_filename(__name__, 'data/samples/sample_pour.txt')}",
            f"file:///{resource_filename(__name__, 'data/samples/uhbox.csv')}",
            f"file:///{resource_filename(__name__, 'data/samples/sample_flow_parameters.nc')}",
            f"file:///{resource_filename(__name__, 'data/samples/sample_routing_domain.nc')}",
            None,
            {"OPTIONS": {"LOG_LEVEL": "CRITICAL",},},
        ),
    ],
)
def test_parameters_local(
    case_id, grid_id, pour_points, uh_box, routing, domain, config_file, config_dict
):
    params = (
        f"case_id={case_id};"
        f"grid_id={grid_id};"
        f"pour_points=@xlink:href={pour_points};"
        f"uh_box=@xlink:href={uh_box};"
        f"routing=@xlink:href={routing};"
        f"domain=@xlink:href={domain};"
        f"config_file=@xlink:href={config_file};"
        f"config_dict=@xlink:href={config_dict};"
    )
    run_wps_process(Parameters(), params)


@pytest.mark.online
@pytest.mark.parametrize(
    (
        "case_id",
        "grid_id",
        "pour_points",
        "uh_box",
        "routing",
        "domain",
        "config_file",
        "config_dict",
    ),
    [
        (
            "sample",
            "COLUMBIA",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/fileServer/datasets/RVIC/sample_pour.txt",
            f"file:///{resource_filename(__name__, 'data/samples/uhbox.csv')}",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/fileServer/datasets/RVIC/sample_flow_parameters.nc",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/fileServer/datasets/RVIC/sample_routing_domain.nc",
            None,
            None,
        ),
        (
            "sample",
            "COLUMBIA",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/fileServer/datasets/RVIC/sample_pour.txt",
            f"file:///{resource_filename(__name__, 'data/samples/uhbox.csv')}",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/fileServer/datasets/RVIC/sample_flow_parameters.nc",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/fileServer/datasets/RVIC/sample_routing_domain.nc",
            f"file:///{resource_filename(__name__, '/data/configs/parameters.cfg')}",
            None,
        ),
        (
            "sample",
            "COLUMBIA",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/fileServer/datasets/RVIC/sample_pour.txt",
            f"file:///{resource_filename(__name__, 'data/samples/uhbox.csv')}",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/fileServer/datasets/RVIC/sample_flow_parameters.nc",
            "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/fileServer/datasets/RVIC/sample_routing_domain.nc",
            None,
            {"OPTIONS": {"LOG_LEVEL": "CRITICAL",},},
        ),
    ],
)
def test_parameters_https(
    case_id, grid_id, pour_points, uh_box, routing, domain, config_file, config_dict
):
    params = (
        f"case_id={case_id};"
        f"grid_id={grid_id};"
        f"pour_points=@xlink:href={pour_points};"
        f"uh_box=@xlink:href={uh_box};"
        f"routing=@xlink:href={routing};"
        f"domain=@xlink:href={domain};"
        f"config_file=@xlink:href={config_file};"
        f"config_dict=@xlink:href={config_dict};"
    )
    run_wps_process(Parameters(), params)
