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
    config_hander,
    get_outfile,
    replace_urls,
    collect_args,
)

# Library imports
import os


class Parameters(Process):
    def __init__(self):
        self.config_template = {
            # configuration dictionary used for RVIC parameters
            # required user inputs are defined as None value
            "OPTIONS": {
                "LOG_LEVEL": "INFO",
                "VERBOSE": True,
                "CLEAN": False,
                "CASEID": None,
                "GRIDID": None,
                "CASE_DIR": None,
                "TEMP_DIR": None,
                "REMAP": False,
                "AGGREGATE": False,
                "AGG_PAD": 25,
                "NETCDF_FORMAT": "NETCDF4",
                "NETCDF_ZLIB": False,
                "NETCDF_COMPLEVEL": 4,
                "NETCDF_SIGFIGS": None,
                "SUBSET_DAYS": None,
                "CONSTRAIN_FRACTIONS": False,
                "SEARCH_FOR_CHANNEL": False,
            },
            "POUR_POINTS": {"FILE_NAME": None,},
            "UH_BOX": {"FILE_NAME": None, "HEADER_LINES": 1,},
            "ROUTING": {
                "FILE_NAME": None,
                "LONGITUDE_VAR": "lon",
                "LATITUDE_VAR": "lat",
                "FLOW_DISTANCE_VAR": "Flow_Distance",
                "FLOW_DIRECTION_VAR": "Flow_Direction",
                "BASIN_ID_VAR": "Basin_ID",
                "VELOCITY": "velocity",
                "DIFFUSION": "diffusion",
                "VELOCITY": 1,
                "DIFFUSION": 2000,
                "OUTPUT_INTERVAL": 86400,
                "BASIN_FLOWDAYS": 100,
                "CELL_FLOWDAYS": 4,
            },
            "DOMAIN": {
                "FILE_NAME": None,
                "LONGITUDE_VAR": "lon",
                "LATITUDE_VAR": "lat",
                "LAND_MASK_VAR": "mask",
                "FRACTION_VAR": "frac",
                "AREA_VAR": "area",
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
                "config_file",
                "Parameters Configuration",
                abstract="Path to input configuration file for Parameters process",
                min_occurs=0,
                max_occurs=1,
                supported_formats=[Format("text/cfg", extension=".cfg")],
            ),
            LiteralInput(
                "config_dict",
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
            log_level,
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

    def config_hander(self, args):
        if "config_file" in args:
            unprocessed = read_config(args["config_file"])
        elif "config_dict" in args:
            unprocessed = args["config_dict"]
        else:
            unprocessed = self.config_template

        processed = self.config_template

        try:
            processed["OPTIONS"]["CASEID"] = args["case_id"]
            processed["OPTIONS"]["GRIDID"] = args["grid_id"]

            for upper_key in unprocessed.keys():
                for lower_key in unprocessed[upper_key].keys():
                    processed[upper_key][lower_key] = unprocessed[upper_key][lower_key]

            if processed["OPTIONS"]["CASE_DIR"] == None:
                processed["OPTIONS"]["CASE_DIR"] = os.path.join(
                    self.workdir, processed["OPTIONS"]["CASEID"]
                )
            if processed["OPTIONS"]["TEMP_DIR"] == None:
                processed["OPTIONS"]["TEMP_DIR"] = (
                    processed["OPTIONS"]["CASEID"] + "/temp"
                )

            processed["POUR_POINTS"]["FILE_NAME"] = args["pour_points"]
            processed["UH_BOX"]["FILE_NAME"] = args["uh_box"]
            processed["ROUTING"]["FILE_NAME"] = args["routing"]
            processed["DOMAIN"]["FILE_NAME"] = args["domain"]

            return processed

        except KeyError:
            raise ProcessError("Invalid config key provided")

    def _handler(self, request, response):
        args = collect_args(request)
        loglevel = args["loglevel"]

        if args["version"]:
            logger.info(version)

        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        config = self.config_hander(args)

        log_handler(
            self,
            response,
            "Creating parameters",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        parameters(config, args["np"])

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
