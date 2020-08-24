import pytest
import requests_mock
from pkg_resources import resource_filename


@pytest.fixture
def make_mock_urls(config, requests_mock):
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
            requests_mock.get(url, content=filedata)
