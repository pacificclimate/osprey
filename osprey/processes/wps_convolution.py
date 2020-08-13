from pywps import Process, LiteralInput, ComplexOutput, FORMATS
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

from rvic.convolution import convolution
from rvic.core.config import read_config
from rvic.version import version

from wps_tools.utils import log_handler
from wps_tools.io import nc_output, log_level
from osprey.utils import logger, config_hander, config_file_builder, run_rvic

from datetime import datetime, timedelta

import os


class Convolution(Process):
    def __init__(self):
        self.config_template = {
            # configuration dictionary used for RVIC convolution
            # required user inputs are defined as None value
            "OPTIONS": {
                "LOG_LEVEL": "INFO",
                "VERBOSE": True,
                "CASE_DIR": None,
                "CASEID": None,
                "CASESTR": "historical",
                "CALENDAR": None,
                "RUN_TYPE": "drystart",  # automatic run
                "RUN_STARTDATE": None,
                "STOP_OPTION": "date",
                "STOP_N": -999,
                "STOP_DATE": None,
                "REST_OPTION": "date",
                "REST_N": -999,
                "REST_DATE": None,
                "REST_NCFORM": "NETCDF4",
            },
            "HISTORY": {
                "RVICHIST_NTAPES": 1,
                "RVICHIST_MFILT": 100000,
                "RVICHIST_NDENS": 1,
                "RVICHIST_NHTFRQ": 1,
                "RVICHIST_AVGFLAG": "A",
                "RVICHIST_OUTTYPE": "array",
                "RVICHIST_NCFORM": "NETCDF4",
                "RVICHIST_UNITS": "m3/s",
            },
            "DOMAIN": {
                "FILE_NAME": None,
                "LONGITUDE_VAR": "lon",
                "LATITUDE_VAR": "lat",
                "AREA_VAR": "area",
                "LAND_MASK_VAR": "mask",
                "FRACTION_VAR": "frac",
            },
            "INITIAL_STATE": {"FILE_NAME": None},
            "PARAM_FILE": {"FILE_NAME": None},
            "INPUT_FORCINGS": {
                "DATL_PATH": None,
                "DATL_FILE": None,
                "TIME_VAR": "time",
                "LATITUDE_VAR": "lat",
                "DATL_LIQ_FLDS": "RUNOFF, BASEFLOW",
                "START": None,
                "END": None,
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
                "config",
                "Configuration",
                abstract="Path to input configuration file or input dictionary",
                data_type="string",
            ),
            log_level,
        ]
        outputs = [
            nc_output,
        ]

        super(Convolution, self).__init__(
            self._handler,
            identifier="convolution",
            title="Flow Convolution",
            abstract="Aggregates the flow contribution from all upstream grid cells"
            "at every timestep lagged according the Impuls Response Functions.",
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    def build_output(self, config):
        case_id = config["OPTIONS"]["CASEID"]
        stop_date = config["OPTIONS"]["STOP_DATE"]
        end_date = str(
            datetime.strptime(stop_date, "%Y-%m-%d").date() + timedelta(days=1)
        )

        directory = os.path.join(config["OPTIONS"]["CASE_DIR"], "hist")
        filename = ".".join([case_id, "rvic", "h0a", end_date, "nc"])
        return os.path.join(directory, filename)

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
        unprocessed = request.inputs["config"][0].data

        log_handler(
            self,
            response,
            "Run Flux Convolution",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        if os.path.isfile(unprocessed):
            config = read_config(unprocessed)
            run_rvic(convolution, version, config, unprocessed)
        else:
            unprocessed = unprocessed.replace("'", '"')
            config = config_hander(self.workdir, unprocessed, self.config_template)
            run_rvic(
                convolution,
                version,
                config,
                config_file_builder(self.workdir, config, self.config_template),
            )

        log_handler(
            self,
            response,
            "Building final flow data output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )
        response.outputs["output"].file = self.build_output(config)

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
