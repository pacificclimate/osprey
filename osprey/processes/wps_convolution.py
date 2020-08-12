from pywps import Process, LiteralInput, ComplexOutput, FORMATS
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

from rvic.convolution import convolution
from rvic.core.config import read_config
from rvic.version import version

from osprey.utils import config_hander, config_file_builder

from datetime import datetime, timedelta

import os
import logging

pywps_logger = logging.getLogger("PYWPS")
stderr_logger = logging.getLogger(__name__)


def log_handler(process, response, message, process_step=None, level="INFO"):
    if process_step:
        status_percentage = process.status_percentage_steps[process_step]
    else:
        status_percentage = response.status_percentage

    # Log to all sources
    pywps_logger.log(getattr(logging, level), message)
    stderr_logger.log(getattr(logging, level), message)
    response.update_status(message, status_percentage=status_percentage)


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
            LiteralInput(
                "loglevel",
                "Log Level",
                default="INFO",
                abstract="Logging level",
                allowed_values=list(logging._levelToName.values()),
            ),
        ]
        outputs = [
            ComplexOutput(
                "output",
                "Output",
                as_reference=True,
                abstract="Output Netcdf File",
                supported_formats=[FORMATS.NETCDF],
            )
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

    def _handler(self, request, response):
        loglevel = request.inputs["loglevel"][0].data
        log_handler(
            self, response, "Starting Process", process_step="start", level=loglevel
        )
        unprocessed = request.inputs["config"][0].data

        log_handler(
            self,
            response,
            "Run Flux Convolution",
            process_step="process",
            level=loglevel,
        )

        if os.path.isfile(unprocessed):
            config = read_config(unprocessed)
            if version == "1.1.0-1":  # RVIC1.1.0.post1
                cfg_filepath = unprocessed
                convolution(cfg_filepath)
            elif version == "1.1.1":  # RVIC1.1.1
                convolution(config)
        else:
            unprocessed = unprocessed.replace("'", '"')
            config = config_hander(self.workdir, unprocessed, self.config_template)
            if version == "1.1.0-1":  # RVIC1.1.0.post1
                cfg_filepath = config_file_builder(
                    self.workdir, config, self.config_template
                )
                convolution(cfg_filepath)
            elif version == "1.1.1":  # RVIC1.1.1
                convolution(config)

        log_handler(
            self,
            response,
            "Building final flow data output",
            process_step="build_output",
            level=loglevel,
        )
        case_id = config["OPTIONS"]["CASEID"]
        stop_date = config["OPTIONS"]["STOP_DATE"]
        end_date = str(
            datetime.strptime(stop_date, "%Y-%m-%d").date() + timedelta(days=1)
        )

        directory = os.path.join(config["OPTIONS"]["CASE_DIR"], "hist")
        filename = ".".join([case_id, "rvic", "h0a", end_date, "nc"])

        response.outputs["output"].file = os.path.join(directory, filename)

        log_handler(
            self, response, "Process Complete", process_step="complete", level=loglevel
        )
        return response
