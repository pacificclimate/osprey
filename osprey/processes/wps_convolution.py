from pywps import Process, LiteralInput, ComplexOutput, FORMATS
from pywps.app.Common import Metadata

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
        config = request.inputs["config"][0].data

        if version == "1.1.1":
            if os.path.isfile(config):
                config_dict = read_config(config)
            else:
                config_dict = json.loads(config)

            log_handler(
                self,
                response,
                "Run Flux Convolution",
                process_step="process",
                level=loglevel,
            )
            convolution(config_dict)

        elif version == "1.1.0-1":
            config_dict = read_config(config)
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
