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
from tempfile import NamedTemporaryFile
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
    prep_csv,
)
from osprey import io

# Library imports
import os


class Parameters(Process):
    def __init__(self):
        self.status_percentage_steps = dict(
            common_status_percentages,
            **{"config_rebuild": 10},
        )
        inputs = [
            log_level,
            io.np,
            io.version,
            io.case_id,
            io.grid_id,
            io.pour_points_csv,
            io.uh_box_csv,
            io.routing,
            io.domain,
            io.params_config_file,
            io.params_config_dict,
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

        uh_box_content = prep_csv(uh_box)
        pour_points_content = prep_csv(pour_points)

        with (
            NamedTemporaryFile(mode="w+", suffix=".csv") as temp_uh_box,
            NamedTemporaryFile(mode="w+", suffix=".csv") as temp_pour_points,
        ):
            temp_uh_box.write(uh_box_content)
            temp_uh_box.seek(0)
            temp_pour_points.write(pour_points_content)
            temp_pour_points.seek(0)

            config = params_config_handler(
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
