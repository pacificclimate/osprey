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
from rvic.core.config import read_config
from wps_tools.utils import log_handler
from wps_tools.io import (
    log_level,
    nc_output,
)
from osprey.utils import (
    logger,
    get_outfile,
    collect_args,
)
from osprey.config_templates import params_config_template

# Library imports
import os


class Parameters(Process):
    def __init__(self):
        self.status_percentage_steps = {
            "start": 0,
            "process": 10,
            "build_output": 95,
            "complete": 100,
        }
        inputs = [
            log_level,
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

    def config_handler(
        self, workdir, case_id, domain, grid_id, pour_points, routing, uh_box, args
    ):
        if "params_config_file" in args:
            unprocessed = read_config(args["params_config_file"])
        elif "params_config_dict" in args:
            unprocessed = eval(args["params_config_dict"])
        else:
            unprocessed = params_config_template

        processed = params_config_template

        try:
            processed["OPTIONS"]["CASEID"] = case_id
            processed["OPTIONS"]["GRIDID"] = grid_id

            for upper_key in unprocessed.keys():
                for lower_key in unprocessed[upper_key].keys():
                    processed[upper_key][lower_key] = unprocessed[upper_key][lower_key]

            if processed["OPTIONS"]["CASE_DIR"] == None:
                processed["OPTIONS"]["CASE_DIR"] = os.path.join(
                    workdir, processed["OPTIONS"]["CASEID"]
                )
            if processed["OPTIONS"]["TEMP_DIR"] == None:
                processed["OPTIONS"]["TEMP_DIR"] = (
                    processed["OPTIONS"]["CASEID"] + "/temp"
                )

            processed["POUR_POINTS"]["FILE_NAME"] = pour_points
            processed["UH_BOX"]["FILE_NAME"] = uh_box
            processed["ROUTING"]["FILE_NAME"] = routing
            processed["DOMAIN"]["FILE_NAME"] = domain

            return processed

        except KeyError:
            raise ProcessError("Invalid config key provided")

    def _handler(self, request, response):
        args = collect_args(request, self.workdir)
        (
            case_id,
            domain,
            grid_id,
            loglevel,
            np,
            pour_points,
            routing,
            uh_box,
            version,
        ) = (
            args[k]
            for k in sorted(args.keys())
            if k != "params_config_file" and k != "params_config_dict"
        )  # Define variables in lexicographic order

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

        config = self.config_handler(
            self.workdir, case_id, domain, grid_id, pour_points, routing, uh_box, args,
        )

        log_handler(
            self,
            response,
            "Creating parameters",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        parameters(config, np)

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
