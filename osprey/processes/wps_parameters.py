# Processor imports
from pywps import (
    Process,
    ComplexInput,
    LiteralInput,
    Format,
    FORMATS,
)
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

# Tool imports
from rvic.version import version
from rvic.parameters import parameters
from wps_tools.logging import log_handler, common_status_percentages
from wps_tools.io import (
    log_level,
    nc_output,
)
from osprey.utils import (
    logger,
    get_outfile,
    collect_args_wrapper,
    params_config_handler,
)

# Library imports
import os


class Parameters(Process):
    def __init__(self):
        self.status_percentage_steps = dict(
            common_status_percentages, **{"config_rebuild": 10},
        )
        inputs = [
            log_level,
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
                "params_config_file",
                "Parameters Configuration",
                abstract="Path to input configuration file for Parameters process",
                min_occurs=0,
                max_occurs=1,
                supported_formats=[Format("text/cfg", extension=".cfg")],
            ),
            LiteralInput(
                "params_config_dict",
                "Parameters Configuration Dictionary",
                abstract="Dictionary containing input configuration for Parameters process",
                min_occurs=0,
                max_occurs=1,
                data_type="string",
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

    def _handler(self, request, response):
        (
            loglevel,
            np,
            version,
            case_id,
            grid_id,
            pour_points,
            uh_box,
            routing,
            domain,
            params_config_file,
            params_config_dict,
        ) = collect_args_wrapper(request, self.workdir, modules=[parameters.__name__])

        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )
        if version:
            logger.info(version)

        log_handler(
            self,
            response,
            "Rebuilding configuration",
            logger,
            log_level=loglevel,
            process_step="config_rebuild",
        )
        config = params_config_handler(
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
            process_step="process",
        )
        try:
            parameters(config, np)
        except Exception as e:
            raise ProcessError(f"{type(e).__name__}: {e}")

        log_handler(
            self,
            response,
            "Building final output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )
        response.outputs["output"].file = get_outfile(config, "params")

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
