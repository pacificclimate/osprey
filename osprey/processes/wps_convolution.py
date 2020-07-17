from pywps import Process, LiteralInput, ComplexOutput, FORMATS
from pywps.app.Common import Metadata

from rvic.convolution import convolution_init, convolution_run, convolution_final
from rvic.core.config import read_config

from datetime import datetime, timedelta

import os
import logging
import json

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

        if os.path.isfile(config):
            config_dict = read_config(config)
        else:
            config_dict = json.loads(config)

        hist_tapes, data_model, rout_var, time_handle, directories = convolution_init(
            config_dict
        )
        time_handle, hist_tapes = convolution_run(
            hist_tapes, data_model, rout_var, time_handle, directories
        )
        convolution_final(time_handle, hist_tapes)

        CASEID = config_dict["OPTIONS"]["CASEID"]
        STOP_DATE = config_dict["OPTIONS"]["STOP_DATE"]
        end_date = str(
            datetime.strptime(STOP_DATE, "%Y-%m-%d").date() + timedelta(days=1)
        )

        directory = directories["hist"]
        filename = ".".join([CASEID, "rvic", "h0a", end_date, "nc"])

        response.outputs["output"].file = self.get_outfile(
            os.path.join(directory, filename)
        )

        return response
