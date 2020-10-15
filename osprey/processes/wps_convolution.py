from pywps import Process, ComplexInput, LiteralInput, ComplexOutput, Format, FORMATS
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

from rvic.convolution import convolution
from rvic.core.config import read_config

from wps_tools.utils import log_handler
from wps_tools.io import nc_output, log_level
from osprey.utils import (
    logger,
    config_hander,
    get_outfile,
)

import os


class Convolution(Process):
    def __init__(self):
        self.config_template = {
            # configuration dictionary used for RVIC convolution
            # required user inputs are defined as None value
            "OPTIONS": {
                "LOG_LEVEL": "INFO",
                "VERBOSE": True,
                "CASE_DIR": None,
                "CASEID": None,
                "CASESTR": "historical",
                "CALENDAR": "standard",
                "RUN_TYPE": "drystart",  # automatic run
                "RUN_STARTDATE": None,
                "STOP_OPTION": "date",
                "STOP_N": -999,
                "STOP_DATE": None,
                "REST_OPTION": "date",
                "REST_N": -999,
                "REST_DATE": None,
                "REST_NCFORM": "NETCDF4",
            },
            "HISTORY": {
                "RVICHIST_NTAPES": 1,
                "RVICHIST_MFILT": 100000,
                "RVICHIST_NDENS": 1,
                "RVICHIST_NHTFRQ": 1,
                "RVICHIST_AVGFLAG": "A",
                "RVICHIST_OUTTYPE": "array",
                "RVICHIST_NCFORM": "NETCDF4",
                "RVICHIST_UNITS": "m3/s",
            },
            "DOMAIN": {
                "FILE_NAME": None,
                "LONGITUDE_VAR": "lon",
                "LATITUDE_VAR": "lat",
                "AREA_VAR": "area",
                "LAND_MASK_VAR": "mask",
                "FRACTION_VAR": "frac",
            },
            "INITIAL_STATE": {"FILE_NAME": None},
            "PARAM_FILE": {"FILE_NAME": None},
            "INPUT_FORCINGS": {
                "DATL_PATH": None,
                "DATL_FILE": None,
                "TIME_VAR": "time",
                "LATITUDE_VAR": "lat",
                "DATL_LIQ_FLDS": ["RUNOFF", "BASEFLOW"],
                "START": None,
                "END": None,
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
                "case_id",
                "Case ID",
                abstract="Case ID for the RVIC process",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
            LiteralInput(
                "start_date",
                "Start Date",
                abstract="Run start date (yyyy-mm-dd-hh). Only used for startup and drystart runs.",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
            LiteralInput(
                "stop_date",
                "Stop Date",
                abstract="Run stop date based on STOP_OPTION",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
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
                "param_file",
                "Parameter File",
                abstract="Path to RVIC parameter file",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            ComplexInput(
                "input_forcings",
                "Input Forcings",
                abstract="Path to land data netCDF forcings",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            ComplexInput(
                "config_file",
                "Convolution Configuration File",
                abstract="Path to input configuration file for Convolution process",
                min_occurs=0,
                max_occurs=1,
                supported_formats=[Format("text/cfg", extension=".cfg")],
            ),
            LiteralInput(
                "config_dict",
                "Convolution Configuration Dictionary",
                abstract="Dictionary containing input configuration for Convolution process",
                min_occurs=0,
                max_occurs=1,
                data_type="string",
            ),
            log_level,
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

    def collect_args(self, request):
        inputs = [request.inputs[k][0] for k in request.inputs.keys()]

        args = {}
        for i in inputs:
            if vars(i)["_file"] != None:
                args[i.identifier] = i.file
            elif vars(i)["_url"] != None:
                args[i.identifier] = i.url
            else:
                args[i.identifier] = i.data

        return args

    def config_hander(self, unprocessed, args):
        """
        This function enables users to provide dictionary-like string for Configuration input.
        If CASE_DIR and REST_DATE are not provided from a user, their values are derived from
        CASEID and STOP_DATE by default.
        """
        processed = self.config_template
        try:
            processed["OPTIONS"]["CASEID"] = args["case_id"]
            processed["OPTIONS"]["RUN_STARTDATE"] = args["start_date"]
            processed["OPTIONS"]["STOP_DATE"] = args["stop_date"]
            processed["DOMAIN"]["FILE_NAME"] = args["domain"]
            processed["PARAM_FILE"]["FILE_NAME"] = args["param_file"]
            processed["INPUT_FORCINGS"]["DATL_PATH"] = "/".join(
                args["input_forcings"].split("/")[0:-1]
            )
            processed["INPUT_FORCINGS"]["DATL_FILE"] = args["input_forcings"].split(
                "/"
            )[-1]

            for upper_key in unprocessed.keys():
                for lower_key in unprocessed[upper_key].keys():
                    processed[upper_key][lower_key] = unprocessed[upper_key][lower_key]

            if processed["OPTIONS"]["CASE_DIR"] == None:
                processed["OPTIONS"]["CASE_DIR"] = os.path.join(
                    self.workdir, processed["OPTIONS"]["CASEID"]
                )
            if processed["OPTIONS"]["REST_DATE"] == None:
                processed["OPTIONS"]["REST_DATE"] = processed["OPTIONS"]["STOP_DATE"]

            return processed

        except KeyError:
            raise ProcessError("Invalid config key provided")

    def _handler(self, request, response):
        args = self.collect_args(request)
        loglevel = args["loglevel"]
        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        if "config_file" in request.inputs.keys():
            unprocessed = read_config(args["config_file"])
        elif "config_dict" in request.inputs.keys():
            unprocessed = eval(args["config_dict"])
        else:
            unprocessed = self.config_template

        config = self.config_hander(unprocessed, args)

        log_handler(
            self,
            response,
            "Run Flux Convolution",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        convolution(config)

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
