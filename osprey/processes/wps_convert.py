from pywps import Process, LiteralInput, ComplexOutput, FORMATS
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

from rvic.convert import convert
from rvic.core.config import read_config

from wps_tools.utils import log_handler
from wps_tools.io import nc_output, log_level
from osprey.utils import (
    logger,
    config_hander,
    get_outfile,
)
import os


class Convert(Process):
    def __init__(self):
        self.config_template = {
            # configuration dictionary used for RVIC convert
            # required user inputs are defined as None value
            "OPTIONS": {
                "LOG_LEVEL": "INFO",
                "VERBOSE": True,
                "CASEID": None,
                "GRIDID": None,
                "CASE_DIR": None,
                "NETCDF_FORMAT": "NETCDF4",
                "SUBSET_DAYS": None,
                "CONSTRAIN_FRACTIONS": False,
            },
            "UHS_FILES": {"ROUT_PROGRAM": "C", "ROUT_DIR": None, "STATION_FILE": None,},
            "ROUTING": {"OUTPUT_INTERVAL": 86400,},
            "DOMAIN": {
                "FILE_NAME": None,
                "LONGITUDE_VAR": "lon",
                "LATITUDE_VAR": "lat",
                "LAND_MASK_VAR": "mask",
                "FRACTION_VAR": "frac",
                "AREA_VAR": "area",
            },
        }
        self.status_percentage_steps = {
            "start": 0,
            "process": 10,
            "build_output": 95,
            "complete": 100,
        }
        inputs = [
            LiteralInput(
                "convert_config",
                "Configuration",
                abstract="Path to input configuration file or input dictionary",
                data_type="string",
            ),
            log_level,
        ]
        outputs = [
            nc_output,
        ]

        super(Convert, self).__init__(
            self._handler,
            identifier="convert",
            title="Parameter Conversion",
            abstract="A simple conversion utility to provide users with the ability to convert old routing model setups into RVIC parameters.",
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    def _handler(self, request, response):
        loglevel = request.inputs["loglevel"][0].data
        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )
        unprocessed = request.inputs["convert_config"][0].data

        log_handler(
            self,
            response,
            "Run Parameter Conversion",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        if os.path.isfile(unprocessed):
            config = read_config(unprocessed)
        else:
            config = config_hander(
                self.workdir, convert.__name__, unprocessed, self.config_template
            )

        convert(config)

        log_handler(
            self,
            response,
            "Building final output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )

        response.outputs["output"].file = get_outfile(config, "params")

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
