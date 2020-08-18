# Processor imports
from pywps import (
    Process,
    LiteralInput,
)
from pywps.app.Common import Metadata

# Tool imports
from rvic import version
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
from osprey.utils import logger

# Library imports
import os
import json
from datetime import datetime


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
            "POUR_POINTS": {
                "FILE_NAME": None,
            },
            "UH_BOX": {
                "FILE_NAME": None,
            },
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
                "LONGITUDE_VAR": "lon"
                "LATITUDE_VAR": "lat"
                "LAND_MASK_VAR": "mask"
                "FRACTION_VAR": "frac"
                "AREA_VAR": "area"
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

    def collect_args(self, request):
        unprocessed = request.inputs["config"][0].data
        np = request.inputs["np"][0].data
        loglevel = request.inputs["loglevel"][0].data
        return (unprocessed, np, loglevel)

    def get_outfile(self, config):
        outdir = os.path.join(config["OPTIONS"]["CASE_DIR"], "params")
        date = datetime.now().strftime("%Y%m%d")
        (param_file,) = collect_output_files(date, outdir)
        return os.path.join(outdir, param_file)

    def _handler(self, request, response):
        if request.inputs["version"][0].data:
            logger.info(version.short_version)

        (unprocessed, np, loglevel) = self.collect_args(request)
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

        if os.path.isfile(unprocessed):
            config = read_config(unprocessed)
            run_rvic(parameters, version, config, unprocessed)
        else:
            unprocessed = unprocessed.replace("'", '"')
            config = config_hander(self.workdir, unprocessed, self.config_template)
            run_rvic(
                parameters,
                version,
                config,
                config_file_builder(self.workdir, config, self.config_template),
            )

        log_handler(
            self,
            response,
            "Building final output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )
        response.outputs["output"].file = self.get_outfile(config)

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
