# Processor imports
from pywps import (
    Process,
    ComplexInput,
    LiteralInput,
    ComplexOutput,
    Format,
    FORMATS,
)

# Tool imports
from rvic.convolution import convolution
from rvic.parameters import parameters
from rvic.core.config import read_config
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError
from osprey.utils import logger, config_hander, get_outfile, replace_urls
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


class FullRVIC(Process):
    def __init__(self):
        self.status_percentage_steps = {
            "start": 0,
            "parameters_process": 10,
            "convolution_process": 20,
            "build_output": 95,
            "complete": 100,
        }
        inputs = [
            ComplexInput(
                "params_config_file",
                "Parameters Configuration",
                abstract="Path to input configuration file or input dictionary",
                min_occurs=0,
                max_occurs=1,
                supported_formats=[FORMATS.TEXT],
            ),
            LiteralInput(
                "params_config_dict",
                "Parameters Configuration",
                abstract="Dictionary containing input configuration for Parameters process",
                min_occurs=0,
                max_occurs=1,
                data_type="string",
            ),
            ComplexInput(
                "convolve_config_file",
                "Convolution Configuration File",
                abstract="Path to input configuration file for Convolution process",
                min_occurs=0,
                max_occurs=1,
                supported_formats=[FORMATS.TEXT],
            ),
            LiteralInput(
                "convolve_config_dict",
                "Convolution Configuration Dictionary",
                abstract="Dictionary containing input configuration for Convolution process",
                min_occurs=0,
                max_occurs=1,
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
        if "params_config_file" in request.inputs.keys():
            logger.critical(vars(request.inputs["params_config_file"][0]))
            logger.critical(request.inputs["params_config_file"][0].file)
            with open(request.inputs["params_config_file"][0].file) as input_file:
                logger.critical(input_file.read())

            params_unprocessed = request.inputs["params_config_file"][0].file
        elif "params_config_dict" in request.inputs.keys():
            params_unprocessed = request.inputs["params_config_dict"][0].data
        else:
            raise ProcessError(
                f"Parameters configuration input (params_config_file/params_config_dict) not provided"
            )

        np = request.inputs["np"][0].data
        loglevel = request.inputs["loglevel"][0].data

        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        if os.path.isfile(params_unprocessed):
            replace_urls(params_unprocessed, self.workdir)
            params_config = read_config(params_unprocessed)
        else:
            params_config = config_hander(
                self.workdir,
                parameters.__name__,
                params_unprocessed,
                Parameters().config_template,
            )

        log_handler(
            self,
            response,
            "Creating parameters",
            logger,
            log_level=loglevel,
            process_step="parameters_process",
        )

        parameters(params_config, np)
        params_output = get_outfile(params_config, "params")

        if "convolve_config_file" in request.inputs.keys():
            logger.critical(vars(request.inputs["convolve_config_file"][0].file))
            logger.critical(request.inputs["convolve_config_file"][0].file)
            with open(request.inputs["convolve_config_file"][0].file) as input_file:
                logger.critical(input_file.read())

            convolve_unprocessed = request.inputs["convolve_config_file"][0].file
        elif "convolve_config_dict" in request.inputs.keys():
            convolve_unprocessed = request.inputs["convolve_config_dict"][0].data
        else:
            raise ProcessError(
                f"Convolution configuration input (convolve_config_file/convolve_config_dict) not provided"
            )

        if os.path.isfile(convolve_unprocessed):
            convolve_config = read_config(convolve_unprocessed)
        else:
            convolve_config = config_hander(
                self.workdir,
                convolution.__name__,
                convolve_unprocessed,
                Convolution().config_template,
            )

        log_handler(
            self,
            response,
            "Run Flux Convolution",
            logger,
            log_level=loglevel,
            process_step="convolution_process",
        )

        convolve_config["PARAM_FILE"]["FILE_NAME"] = params_output
        convolution(convolve_config)

        log_handler(
            self,
            response,
            "Building final flow data output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )

        response.outputs["output"].file = get_outfile(convolve_config, "hist")

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )

        return response
