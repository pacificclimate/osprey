from pywps import Process, LiteralInput, LiteralOutput, UOM
from pywps.app.Common import Metadata

import logging

LOGGER = logging.getLogger("PYWPS")


class Convolution(Process):
    def __init__(self):
        inputs = [
            LiteralInput(
                "name",
                "Your name",
                abstract="Please enter your name.",
                keywords=["name", "firstname"],
                data_type="string",
            )
        ]
        outputs = [
            LiteralOutput(
                "output",
                "Output response",
                abstract="A friendly Hello from us.",
                keywords=["output", "result", "response"],
                data_type="string",
            )
        ]

        super(Convolution, self).__init__(
            self._handler,
            identifier="convolution",
            title="Flow Convolution",
            abstract="Aggregates the flow contribution from all upstream grid cells at every timestep lagged according the Impuls Response Functions.",
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    @staticmethod
    def _handler(request, response):
        LOGGER.info("say hello")
        response.outputs["output"].data = "Hello " + request.inputs["name"][0].data
        response.outputs["output"].uom = UOM("unity")
        return response
