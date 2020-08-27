import pytest
from pkg_resources import resource_filename


def make_mock_urls(config, requests_mock):
    """Create mock get requests for urls in
    config file

    Since it is possible for a test file to not
    exist on THREDDS, requests_mock is used to
    get these urls, and their content is the corresponding
    data coming from the same file in local storage.

    Parameters:
        config (str): Path to config file
        requests_mock: requests_mock fixture
    """
    read_config = open(config, "r")
    config_data = read_config.readlines()
    read_config.close()
    for line in config_data:
        if "https" in line:
            url = line.split(" ")[-1]  # https url is last word in line
            url = url.rstrip()  # remove \n character at end
            filename = url.split("/")[-1]
            f = open(resource_filename("tests", f"data/samples/{filename}"), "rb")
            filedata = f.read()
            f.close()
            requests_mock.get(url, content=filedata)
