from pywps import Process, LiteralInput, ComplexOutput, FORMATS
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

from rvic.convolution import convolution
from rvic.core.config import read_config
from rvic.version import version

from datetime import datetime, timedelta

import os
import logging
import json

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
        self.config_dict = {
            # configuration dictionary used for RVIC convolution
            # required user inputs are defined as None value
            "OPTIONS": {
                "LOG_LEVEL": "INFO",
                "VERBOSE": True,
                "CASE_DIR": None,
                "CASEID": None,
                "CASESTR": "historical",
                "CALENDAR": "standard",
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

    def config_dict_hander(self, config):
        """
        This function enables users to provide dictionary-like string for Configuration input.
        If CASE_DIR and REST_DATE are not provided from a user, their values are derived from
        CASEID and STOP_DATE by default.
        """
        input_dict = json.loads(config)
        try:
            for upper_key in input_dict.keys():
                for lower_key in input_dict[upper_key].keys():
                    self.config_dict[upper_key][lower_key] = input_dict[upper_key][
                        lower_key
                    ]

            if self.config_dict["OPTIONS"]["CASE_DIR"] == None:
                self.config_dict["OPTIONS"]["CASE_DIR"] = os.path.join(
                    self.workdir, self.config_dict["OPTIONS"]["CASEID"]
                )
            if self.config_dict["OPTIONS"]["REST_DATE"] == None:
                self.config_dict["OPTIONS"]["REST_DATE"] = self.config_dict["OPTIONS"][
                    "STOP_DATE"
                ]

        except KeyError as e:
            raise ProcessError(f"Invalid config key provided")

    def config_file_builder(self, config_dict):
        """
        This function is used for RVIC1.1.0.post1 only since the version requires Configuration input
        to be a .cfg filepath. The function uses information from config_dict to create the file.
        """
        cfg_filepath = os.path.join(self.workdir, "convolve_file.cfg")
        with open(cfg_filepath, "w") as cfg_file:
            for upper_key in self.config_dict.keys():
                cfg_file.write(f"[{upper_key}]\n")
                for k, v in self.config_dict[upper_key].items():
                    cfg_file.write(f"{k}: {str(v)}\n")

        return cfg_filepath

    def _handler(self, request, response):
        loglevel = request.inputs["loglevel"][0].data
        log_handler(
            self, response, "Starting Process", process_step="start", level=loglevel
        )
        config = request.inputs["config"][0].data

        if os.path.isfile(config):
            config_dict = read_config(config)
        else:
            config = config.replace("'", '"')
            self.config_dict_hander(config)
            config_dict = self.config_dict
            if version == "1.1.0-1":  # RVIC1.1.0.post1
                config = self.config_file_builder(config_dict)

        log_handler(
            self,
            response,
            "Run Flux Convolution",
            process_step="process",
            level=loglevel,
        )
        convolution(config)

        log_handler(
            self,
            response,
            "Building final flow data output",
            process_step="build_output",
            level=loglevel,
        )
        case_id = config_dict["OPTIONS"]["CASEID"]
        stop_date = config_dict["OPTIONS"]["STOP_DATE"]
        end_date = str(
            datetime.strptime(stop_date, "%Y-%m-%d").date() + timedelta(days=1)
        )

        directory = os.path.join(config_dict["OPTIONS"]["CASE_DIR"], "hist")
        filename = ".".join([case_id, "rvic", "h0a", end_date, "nc"])

        response.outputs["output"].file = os.path.join(directory, filename)

        log_handler(
            self, response, "Process Complete", process_step="complete", level=loglevel
        )
        return response
