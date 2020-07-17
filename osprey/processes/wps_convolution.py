from pywps import Process, LiteralInput, ComplexOutput, FORMATS
from pywps.app.Common import Metadata

from rvic.convolution import convolution_init, convolution_run, convolution_final
from rvic.core.config import read_config

import os
import logging

LOGGER = logging.getLogger("PYWPS")


class Convolution(Process):
    def __init__(self):
        inputs = [
            LiteralInput(
                "config",
                "Configuration",
                abstract="Path to input configuration file or input dictionary",
                data_type="string",
            ),
        ]
        outputs = [
            ComplexOutput(
                "output",
                "Output",
                as_reference=True,
                abstract="Output Netcdf File",
                supported_formats=[FORMATS.NETCDF],
            )
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
        config = request.inputs["config"][0].data

        if not os.path.isfile(config):
            raise IOError("config_file: {0} does not " "exist".format(config))

        hist_tapes, data_model, rout_var, time_handle, directories = convolution_init(
            config
        )
        time_handle, hist_tapes = convolution_run(
            hist_tapes, data_model, rout_var, time_handle, directories
        )
        convolution_final(time_handle, hist_tapes)

        response.outputs["output"].file = self.get_outfile(
            "sample.rvic.h0a.2013-01-01.nc"
        )

        return response
