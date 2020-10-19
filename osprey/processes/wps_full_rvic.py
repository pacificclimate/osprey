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
from osprey.utils import logger, get_outfile, collect_args
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
            log_level,
            LiteralInput(
                "case_id",
                "Case ID",
                abstract="Case ID for the RVIC process (required)",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
            LiteralInput(
                "grid_id",
                "GRID ID",
                abstract="Routing domain grid shortname (required)",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
            LiteralInput(
                "run_startdate",
                "Run Start Date",
                abstract="Run start date (yyyy-mm-dd-hh). Only used for startup and drystart runs. (required)",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
            LiteralInput(
                "stop_date",
                "Stop Date",
                abstract="Run stop date based on STOP_OPTION (required)",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
            ComplexInput(
                "pour_points",
                "POUR POINTS",
                abstract="Path to Pour Points File; A comma separated file of outlets to route to [lons, lats] (required)",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.TEXT, Format("text/csv", extension=".csv")],
            ),
            ComplexInput(
                "uh_box",
                "UH BOX",
                abstract="Path to UH Box File. This defines the unit hydrograph to rout flow to the edge of each grid cell. (required)",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.TEXT, Format("text/csv", extension=".csv")],
            ),
            ComplexInput(
                "routing",
                "ROUTING",
                abstract="Path to routing inputs netCDF. (required)",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            ComplexInput(
                "domain",
                "Domain",
                abstract="Path to CESM complaint domain file (required)",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            ComplexInput(
                "input_forcings",
                "Input Forcings",
                abstract="Path to land data netCDF forcings (required)",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            ComplexInput(
                "params_config_file",
                "Parameters Configuration",
                abstract="Path to input configuration file or input dictionary (optional)",
                min_occurs=0,
                max_occurs=1,
                supported_formats=[Format("text/cfg", extension=".cfg")],
            ),
            LiteralInput(
                "params_config_dict",
                "Parameters Configuration",
                abstract="Dictionary containing input configuration for Parameters process (optional)",
                min_occurs=0,
                max_occurs=1,
                data_type="string",
            ),
            ComplexInput(
                "convolve_config_file",
                "Convolution Configuration File",
                abstract="Path to input configuration file for Convolution process (optional)",
                min_occurs=0,
                max_occurs=1,
                supported_formats=[Format("text/cfg", extension=".cfg")],
            ),
            LiteralInput(
                "convolve_config_dict",
                "Convolution Configuration Dictionary",
                abstract="Dictionary containing input configuration for Convolution process (optional)",
                min_occurs=0,
                max_occurs=1,
                data_type="string",
            ),
            LiteralInput(
                "version",
                "Version",
                default=True,
                abstract="Return RVIC version string (optional)",
                data_type="boolean",
            ),
            LiteralInput(
                "np",
                "numofproc",
                default=1,
                abstract="Number of processors used to run job (optional)",
                data_type="integer",
            ),
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
        args = collect_args(request, self.workdir)
        loglevel = args["loglevel"]

        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        params_config = Parameters().config_handler(self.workdir, args)

        log_handler(
            self,
            response,
            "Creating parameters",
            logger,
            log_level=loglevel,
            process_step="parameters_process",
        )

        parameters(params_config, args["np"])
        params_output = get_outfile(params_config, "params")
        args["param_file"] = params_output

        log_handler(
            self,
            response,
            "Run Flux Convolution",
            logger,
            log_level=loglevel,
            process_step="convolution_process",
        )

        convolve_config = Convolution().config_handler(self.workdir, args)
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
