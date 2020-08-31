# Processor imports
from pywps import (
    Process,
    LiteralInput,
    ComplexOutput,
    FORMATS,
)

# Tool imports
from rvic import version
from rvic.convolution import convolution
from rvic.parameters import parameters
from rvic.core.config import read_config
from pywps.app.Common import Metadata
from osprey.utils import logger, config_hander, get_outfile
from osprey.processes.wps_parameters import Parameters
from osprey.processes.wps_convolution import Convolution
from wps_tools.utils import (
    collect_output_files,
    log_handler,
)
from wps_tools.io import (
    log_level,
    nc_output,
)
import os
from json import loads, dumps


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
                "version",
                "Version",
                default=True,
                abstract="Return RVIC version string",
                data_type="boolean",
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

        params_output = Parameters()._handler(request, response)

        unprocessed = request.inputs["convolve_config"][0].data
        if os.path.isfile(unprocessed):
            config = loads(dumps(read_config(unprocessed)))

        else:
            unprocessed = unprocessed.replace("'", '"')
            config = config_hander(
                self.workdir,
                convolution.__name__,
                unprocessed,
                Convolution().config_template,
            )

        config["PARAM_FILE"]["FILE_NAME"] = params_output
        request.inputs["convolve_config"][0].data = config

        convolve_output = Convolution()._handler(request, response)
        response.outputs["output"].file = convolve_output

        return response
