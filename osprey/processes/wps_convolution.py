from pywps import Process, ComplexInput, LiteralInput, ComplexOutput, Format, FORMATS
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

from rvic.convolution import convolution

from wps_tools.logging import log_handler, common_status_percentages
from wps_tools.io import nc_output, log_level
from osprey.utils import (
    logger,
    get_outfile,
    collect_args_wrapper,
    convolve_config_handler,
)
from osprey import io


class Convolution(Process):
    def __init__(self):
        self.status_percentage_steps = dict(
            common_status_percentages,
            **{"config_rebuild": 10},
        )
        inputs = [
            log_level,
            io.case_id,
            io.run_startdate,
            io.stop_date,
            io.domain,
            ComplexInput(
                "param_file",
                "Parameter File",
                abstract="Path to RVIC parameter file",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            io.input_forcings,
            io.convolve_config_file,
            io.convolve_config_dict,
        ]
        outputs = [
            nc_output,
        ]

        super(Convolution, self).__init__(
            self._handler,
            identifier="convolution",
            title="Flow Convolution",
            abstract="Aggregates the flow contribution from all upstream grid cells"
            "at every timestep lagged according the Impuls Response Functions.",
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    def _handler(self, request, response):
        (
            loglevel,
            case_id,
            run_startdate,
            stop_date,
            domain,
            param_file,
            input_forcings,
            convolve_config_file,
            convolve_config_dict,
        ) = collect_args_wrapper(request, self.workdir, modules=[convolution.__name__])

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
        config = convolve_config_handler(
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

        log_handler(
            self,
            response,
            "Run Flux Convolution",
            logger,
            log_level=loglevel,
            process_step="process",
        )
        try:
            convolution(config)
        except Exception as e:
            raise ProcessError(f"{type(e).__name__}: {e}")

        log_handler(
            self,
            response,
            "Building final flow data output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )
        response.outputs["output"].file = get_outfile(config, "hist")

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
