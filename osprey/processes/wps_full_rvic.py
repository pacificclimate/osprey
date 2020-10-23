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
from rvic.core.log import close_logger

from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError
from osprey.utils import (
    logger,
    get_outfile,
    collect_args,
    convolve_config_handler,
    params_config_handler,
)
from wps_tools.utils import log_handler
from wps_tools.io import (
    log_level,
    nc_output,
)


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
            LiteralInput(
                "case_id",
                "Case ID",
                abstract="Case ID for the RVIC process",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
            LiteralInput(
                "grid_id",
                "GRID ID",
                abstract="Routing domain grid shortname",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
            LiteralInput(
                "run_startdate",
                "Run Start Date",
                abstract="Run start date (yyyy-mm-dd-hh). Only used for startup and drystart runs.",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
            LiteralInput(
                "stop_date",
                "Stop Date",
                abstract="Run stop date based on STOP_OPTION",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
            ComplexInput(
                "pour_points",
                "POUR POINTS",
                abstract="Path to Pour Points File; A comma separated file of outlets to route to [lons, lats]",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.TEXT, Format("text/csv", extension=".csv")],
            ),
            ComplexInput(
                "uh_box",
                "UH BOX",
                abstract="Path to UH Box File. This defines the unit hydrograph to rout flow to the edge of each grid cell.",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.TEXT, Format("text/csv", extension=".csv")],
            ),
            ComplexInput(
                "routing",
                "ROUTING",
                abstract="Path to routing inputs netCDF.",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            ComplexInput(
                "domain",
                "Domain",
                abstract="Path to CESM complaint domain file",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            ComplexInput(
                "input_forcings",
                "Input Forcings",
                abstract="Path to land data netCDF forcings",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            ComplexInput(
                "params_config_file",
                "Parameters Configuration",
                abstract="Path to input configuration file or input dictionary",
                min_occurs=0,
                max_occurs=1,
                supported_formats=[Format("text/cfg", extension=".cfg")],
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
                supported_formats=[Format("text/cfg", extension=".cfg")],
            ),
            LiteralInput(
                "convolve_config_dict",
                "Convolution Configuration Dictionary",
                abstract="Dictionary containing input configuration for Convolution process",
                min_occurs=0,
                max_occurs=1,
                data_type="string",
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
        (
            loglevel,
            version,
            np,
            case_id,
            grid_id,
            run_startdate,
            stop_date,
            pour_points,
            uh_box,
            routing,
            domain,
            input_forcings,
            params_config_file,
            params_config_dict,
            convolve_config_file,
            convolve_config_dict,
        ) = collect_args(
            request, self.workdir, modules=[parameters.__name__, convolution.__name__]
        )

        if version:
            logger.info(version)

        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        params_config = params_config_handler(
            self.workdir,
            case_id,
            domain,
            grid_id,
            pour_points,
            routing,
            uh_box,
            params_config_file,
            params_config_dict,
        )

        log_handler(
            self,
            response,
            "Creating parameters",
            logger,
            log_level=loglevel,
            process_step="parameters_process",
        )
        try:
            parameters(params_config, np)
        except RecursionError:
            close_logger()

        params_output = get_outfile(params_config, "params")
        param_file = params_output

        log_handler(
            self,
            response,
            "Run Flux Convolution",
            logger,
            log_level=loglevel,
            process_step="convolution_process",
        )

        convolve_config = convolve_config_handler(
            self.workdir,
            case_id,
            run_startdate,
            stop_date,
            domain,
            param_file,
            input_forcings,
            convolve_config_file,
            convolve_config_dict,
        )

        try:
            convolution(convolve_config)
        except RecursionError:
            close_logger()

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
