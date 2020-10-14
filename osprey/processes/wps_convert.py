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
            ComplexInput(
                "config_file",
                "Convert Configuration",
                abstract="Path to input configuration file for Convert process",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.TEXT],
            ),
            log_level,
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

    def _handler(self, request, response):
        loglevel = request.inputs["loglevel"][0].data
        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )
        logger.critical(vars(request.inputs["config_file"][0]))
        config_file = request.inputs["config_file"][0].file

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
