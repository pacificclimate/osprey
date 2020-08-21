from pkg_resources import resource_filename
import os
import pytest
import requests_mock
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process
from osprey.processes.wps_parameters import Parameters
from osprey.utils import replace_filenames


def make_mock_urls(config, m):
    read_config = open(config, "r")
    config_data = read_config.readlines()
    read_config.close()
    for line in config_data:
        if "https" in line:
            url = line.split(" ")[-1]  # https url is last word in line
            url = url.rstrip()  # remove \n character at end
            filename = url.split("/")[-1]
            f = open(resource_filename(__name__, f"data/samples/{filename}"), "rb")
            filedata = f.read()
            f.close()
            m.get(url, content=filedata)


@pytest.mark.parametrize(
    ("config"),
    [resource_filename(__name__, "data/samples/sample_parameter_config.cfg")],
)
def test_parameters_local(config):
    config_name = os.path.splitext(config)[0]  # Remove .cfg extension
    with NamedTemporaryFile(
        suffix=".cfg", prefix=os.path.basename(config_name), mode="w+t"
    ) as temp_config:
        replace_filenames(config, temp_config)
        temp_config.read()
        params = f"config={temp_config.name};"
        run_wps_process(Parameters(), params)


@pytest.mark.online
@pytest.mark.parametrize(
    ("config"), [resource_filename(__name__, "configs/parameter_https.cfg")],
)
@requests_mock.Mocker(kw="mock")
def test_parameters_https(config, **kwargs):
    m = kwargs["mock"]
    make_mock_urls(config, m)
    config_name = os.path.splitext(config)[0]  # Remove .cfg extension
    with NamedTemporaryFile(
        suffix=".cfg", prefix=os.path.basename(config_name), mode="w+t"
    ) as temp_config:  # Avoid permanent replacement of https URLs
        read_config = open(config, "r")
        temp_config.writelines(read_config.read())
        temp_config.read()
        params = f"config={temp_config.name};"
        run_wps_process(Parameters(), params)
