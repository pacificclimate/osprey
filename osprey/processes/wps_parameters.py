# Processor imports
from pywps import (
    Process,
    LiteralInput,
)
from pywps.app.Common import Metadata

# Tool imports
from rvic.parameters import parameters
from rvic.core.config import read_config
from wps_tools.utils import (
    collect_output_files,
    log_handler,
)
from wps_tools.io import (
    log_level,
    nc_output,
)

# Library imports
import logging
import os
import json

pywps_logger = logging.getLogger("PYWPS")


class Parameters(Process):
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
                "np",
                "numofproc",
                default=1,
                abstract="Number of processors used to run job",
                data_type="integer",
            ),
            LiteralInput(
                "version",
                "Version",
                default=True,
                abstract="Return RVIC version string",
                data_type="boolean",
            ),
        ]
        outputs = [
            nc_output,
        ]

        super(Parameters, self).__init__(
            self._handler,
            identifier="parameters",
            title="Parameters",
            abstract="Develop impulse response functions using inputs from a "
            "configuration file or dictionary",
            metadata=[
                Metadata("NetCDF processing"),
                Metadata("Climate Data Operations"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    def collect_args(self, request):
        config = request.inputs["config"][0].data
        np = request.inputs["np"][0].data
        return (config_file, np)

    def get_outfile(self, config):
        if os.path.isfile(config):
            config_dict = read_config(config)
        else:
            config_dict = json.loads(config)  # config is dictionary of inputs
        outdir = os.path.join(config_dict["OPTIONS"]["CASE_DIR"], "params")
        (param_file,) = collect_output_files("rvic", outdir)
        return os.path.join(outdir, param_file)

    def _handler(self, request, response):
        if request.inputs["version"][0].data:
            from rvic import version

            pywps_logger.info(version.short_version)

        (config, np) = self.collect_args(request)
        log_handler(
            self, response, "Starting Process", process_step="start", level=loglevel
        )

        log_handler(
            self,
            response,
            "Creating parameters",
            process_step="process",
            level=loglevel,
        )
        parameters(config, np)

        log_handler(
            self,
            response,
            "Building final output",
            process_step="build_output",
            level=loglevel,
        )
        response.outputs["output"].file = self.get_outfile(config)

        log_handler(
            self, response, "Process Complete", process_step="complete", level=loglevel,
        )
        return response
