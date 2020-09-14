from pkg_resources import resource_filename
import os
import pytest
from tempfile import NamedTemporaryFile

from wps_tools.testing import run_wps_process
from osprey.processes.wps_parameters import Parameters
from osprey.utils import replace_filenames


@pytest.mark.parametrize(
    ("config"),
    [
        resource_filename(__name__, "data/configs/parameters_local.cfg"),
        {
            "OPTIONS": {"CASEID": "sample", "GRIDID": "COLUMBIA",},
            "POUR_POINTS": {
                "FILE_NAME": resource_filename(__name__, "data/samples/sample_pour.txt")
            },
            "UH_BOX": {
                "FILE_NAME": resource_filename(__name__, "data/samples/uhbox.csv")
            },
            "ROUTING": {
                "FILE_NAME": resource_filename(
                    __name__, "data/samples/sample_flow_parameters.nc"
                )
            },
            "DOMAIN": {
                "FILE_NAME": resource_filename(
                    __name__, "data/samples/sample_routing_domain.nc"
                )
            },
        },
    ],
)
def test_parameters_local(config):
    if type(config) == dict:
        params = ("config={0};").format(config)
        run_wps_process(Parameters(), params)
    else:
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
    ("config"), [resource_filename(__name__, "data/configs/parameters_https.cfg")],
)
def test_parameters_https(config, conftest_make_mock_urls):
    config_name = os.path.splitext(config)[0]  # Remove .cfg extension
    with NamedTemporaryFile(
        suffix=".cfg", prefix=os.path.basename(config_name), mode="w+t"
    ) as temp_config:  # Avoid permanent replacement of https URLs
        read_config = open(config, "r")
        temp_config.writelines(read_config.read())
        temp_config.read()
        params = f"config={temp_config.name};"
        run_wps_process(Parameters(), params)
