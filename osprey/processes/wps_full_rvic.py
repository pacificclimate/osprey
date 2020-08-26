# Processor imports
from pywps import (
    Process,
    LiteralInput,
)

# Tool imports
from rvic import version
from pywps.app.Common import Metadata
from osprey.processes.wps_convolution import Convolution
from osprey.processes.wps_parameters import Parameters
from osprey.utils import logger
from wps_tools.utils import (
    collect_output_files,
    log_handler,
)
from wps_tools.io import (
    log_level,
    nc_output,
)

class FullRVIC(Process):
    def __init__(self):
        self.status_percentage_steps = {
            "start": 0,
            "process": 10,
            "build_output": 95,
            "complete": 100,
        }
        inputs = [
            LiteralInput(
                "params_config",
                "Parameters Configuration",
                abstract="Path to parameters module's input configuration file or input dictionary",
                data_type="string",
            ),
            LiteralInput(
                "convolve_config",
                "Convolution Configuration",
                abstract="Path to convolution module's input configuration file or input dictionary",
                data_type="string",
            ),
            LiteralInput(
                "np",
                "numofproc",
                default=1,
                abstract="Number of processors used to run job",
                data_type="integer",
            ),
            log_level,
        ]
        outputs = [
            nc_output,
        ]

        super(FullRVIC, self).__init__(
            self._handler,
            identifier="full_rvic",
            title="Full RVIC",
            abstract="Run full RVIC process combining Parameters and Convolution modules",
            metadata=[
                Metadata("NetCDF processing"),
                Metadata("Climate Data Operations"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    def _handler(self, request, response):
        if request.inputs["version"][0].data:
            logger.info(version.short_version)

        loglevel = request.inputs["loglevel"][0].data

        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        log_handler(
            self,
            response,
            "Creating parameters",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        log_handler(
            self,
            response,
            "Building final output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        
        return response