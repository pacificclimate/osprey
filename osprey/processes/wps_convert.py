from pywps import Process, ComplexInput, ComplexOutput, Format, FORMATS
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

from rvic.convert import convert
from rvic.core.config import read_config

from wps_tools.logging import log_handler, common_status_percentages
from wps_tools.io import nc_output, log_level
from osprey.utils import (
    logger,
    get_outfile,
    collect_args_wrapper,
)
import os
import configparser


class Convert(Process):
    def __init__(self):
        self.status_percentage_steps = dict(
            common_status_percentages, **{"config_rebuild": 10},
        )
        inputs = [
            log_level,
            ComplexInput(
                "uhs_files",
                "UHS_Files",
                abstract="Path to UHS file",
                min_occurs=1,
                supported_formats=[Format('text/plain', extension='.uhs_s2'),],
            ),
            ComplexInput(
                "station_file",
                "Station_FILE",
                abstract="Path to stations file",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.TEXT],
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
                "Convert Configuration",
                abstract="Path to input configuration file for Convert process",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[Format("text/cfg", extension=".cfg")],
            ),
        ]
        outputs = [
            nc_output,
        ]

        super(Convert, self).__init__(
            self._handler,
            identifier="convert",
            title="Parameter Conversion",
            abstract="A simple conversion utility to provide users with the ability to convert old routing model setups into RVIC parameters.",
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    def edit_config_file(self, config_file, uhs_files, station_file, domain):
        parser = configparser.ConfigParser()
        parser.optionxform = str

        unprocessed = config_file
        config_dict = read_config(unprocessed)
        for section in config_dict.keys():
            parser[section] = {
                k: str(config_dict[section][k]) for k in config_dict[section].keys()
            }

        try:
            parser["UHS_FILES"]["ROUT_DIR"] = "/".join(uhs_files.split("/")[:-1])
            parser["UHS_FILES"]["STATION_FILE"] = station_file
            parser["DOMAIN"]["FILE_NAME"] = domain
        except KeyError as e:
            raise ProcessError(
                f"{type(e).__name__}: Invalid header or config key in config file"
            )

        processed = ".".join(unprocessed.split(".")[:-1]) + "_edited.cfg"
        with open(processed, "w") as cfg:
            parser.write(cfg)

        return processed

    def _handler(self, request, response):
        loglevel, uhs_files, station_file, domain, config_file = collect_args_wrapper(
            request, self.workdir
        )

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
            "Rebuilding configuration",
            logger,
            log_level=loglevel,
            process_step="config_rebuild",
        )
        config_file = self.edit_config_file(
            config_file, uhs_files, station_file, domain
        )

        log_handler(
            self,
            response,
            "Run Parameter Conversion",
            logger,
            log_level=loglevel,
            process_step="process",
        )
        try:
            convert(config_file)
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
        config = read_config(config_file)
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
