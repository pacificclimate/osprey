from pywps import Process, ComplexInput, LiteralInput, ComplexOutput, Format, FORMATS
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

from rvic.convert import convert
from rvic.core.config import read_config

from wps_tools.utils import log_handler
from wps_tools.io import nc_output, log_level
from osprey.utils import (
    logger,
    get_outfile,
    replace_urls,
    collect_args,
)
import os


class Convert(Process):
    def __init__(self):
        self.status_percentage_steps = {
            "start": 0,
            "process": 10,
            "build_output": 95,
            "complete": 100,
        }
        inputs = [
            log_level,
            ComplexInput(
                "uhs_files",
                "UHS_Files",
                abstract="Path to UHS file (required)",
                min_occurs=1,
                supported_formats=[FORMATS.TEXT],
            ),
            ComplexInput(
                "station_file",
                "Station_FILE",
                abstract="Path to stations file (required)",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.TEXT],
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
                "config_file",
                "Convert Configuration",
                abstract="Path to input configuration file for Convert process (optional)",
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

    def edit_config_file(self, args):
        config_file = args["config_file"]
        with open(config_file, "r") as cf:
            lines = cf.read().split("\n")
            for idx, line in enumerate(lines):
                if line.startswith("ROUT_DIR"):
                    lines[idx] = "ROUT_DIR:" + "/".join(
                        args["uhs_files"].split("/")[:-1]
                    )
                elif line.startswith("STATION_FILE"):
                    lines[idx] = "STATION_FILE:" + args["station_file"]
                    print(line)
                elif line.startswith("FILE_NAME"):
                    lines[idx] = "FILE_NAME:" + args["domain"]

        config_data = "\n".join(lines)
        with open(config_file, "w") as cf:
            cf.write(config_data)

        return config_file

    def _handler(self, request, response):
        args = collect_args(request)
        loglevel = args["loglevel"]

        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        config_file = self.edit_config_file(args)

        log_handler(
            self,
            response,
            "Run Parameter Conversion",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        tmp_config_file = replace_urls(config_file, self.workdir)
        convert(tmp_config_file)

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
