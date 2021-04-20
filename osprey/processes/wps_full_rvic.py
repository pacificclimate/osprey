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

from tempfile import NamedTemporaryFile
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError
from osprey.utils import (
    logger,
    get_outfile,
    collect_args_wrapper,
    convolve_config_handler,
    params_config_handler,
    prep_csv,
)
from osprey import io
from wps_tools.logging import log_handler, common_status_percentages
from wps_tools.io import log_level, nc_output


class FullRVIC(Process):
    def __init__(self):
        self.status_percentage_steps = dict(
            common_status_percentages,
            **{
                "params_config_rebuild": 5,
                "params_process": 10,
                "params_build": 15,
                "convolve_config_rebuild": 20,
                "convolution_process": 25,
            },
        )
        inputs = [
            log_level,
            io.version,
            io.np,
            io.case_id,
            io.grid_id,
            io.run_startdate,
            io.stop_date,
            io.pour_points_csv,
            io.uh_box_csv,
            io.routing,
            io.domain,
            io.input_forcings,
            io.params_config_file,
            io.params_config_dict,
            io.convolve_config_file,
            io.convolve_config_dict,
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
        ) = collect_args_wrapper(
            request, self.workdir, modules=[parameters.__name__, convolution.__name__]
        )

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
            "Rebuilding Parameters configuration",
            logger,
            log_level=loglevel,
            process_step="params_config_rebuild",
        )

        uh_box_content = prep_csv(uh_box)
        pour_points_content = prep_csv(pour_points)

        with NamedTemporaryFile(
            mode="w+", suffix=".csv"
        ) as temp_uh_box, NamedTemporaryFile(
            mode="w+", suffix=".csv"
        ) as temp_pour_points:
            temp_uh_box.write(uh_box_content)
            temp_uh_box.seek(0)
            temp_pour_points.write(pour_points_content)
            temp_pour_points.seek(0)

            params_config = params_config_handler(
                self.workdir,
                case_id,
                domain,
                grid_id,
                temp_pour_points.name,
                routing,
                temp_uh_box.name,
                params_config_file,
                params_config_dict,
            )

            log_handler(
                self,
                response,
                "Processing parameters",
                logger,
                log_level=loglevel,
                process_step="params_process",
            )
            try:
                parameters(params_config, np)
            except Exception as e:
                raise ProcessError(f"{type(e).__name__}: {e}")

        log_handler(
            self,
            response,
            "Building parameters file",
            logger,
            log_level=loglevel,
            process_step="params_build",
        )
        params_file = get_outfile(params_config, "params")

        log_handler(
            self,
            response,
            "Rebuilding Convolution configuration",
            logger,
            log_level=loglevel,
            process_step="convolve_config_rebuild",
        )
        convolve_config = convolve_config_handler(
            self.workdir,
            case_id,
            run_startdate,
            stop_date,
            domain,
            params_file,
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
            process_step="convolution_process",
        )
        try:
            convolution(convolve_config)
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
