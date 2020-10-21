from pkg_resources import resource_filename
from pywps.app.exceptions import ProcessError
import logging
import os
from urllib.parse import urlparse
from urllib.request import urlretrieve
from datetime import datetime, timedelta
from collections.abc import Iterable
from wps_tools.utils import collect_output_files, is_opendap_url
from tempfile import NamedTemporaryFile
from .config_templates import convolve_config_template, params_config_template
from rvic.core.config import read_config

logger = logging.getLogger("PYWPS")
logger.setLevel(logging.NOTSET)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: osprey: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_outfile(config, dir_name):
    """
    This function returns the output filepath of RVIC processes.
    Parameters
        1. config (dict): Set of key-value pairs that contains the information of filename
            parameters file: CASEID.rvic.prm.GRIDID.DATE.nc
            convolution file: CASEID.rvic.h0a.ENDINGDATE.nc
        2. dir_name (str): name of the directory that te output file will be stored.
            parameters module   --->    dir_name == "params"
            convoltion module   --->    dir_name == "hist"
    """
    case_id = config["OPTIONS"]["CASEID"]
    case_dir = config["OPTIONS"]["CASE_DIR"]
    if dir_name == "params":
        grid_id = config["OPTIONS"]["GRIDID"]
        date = datetime.now().strftime("%Y%m%d")
        filename = ".".join([case_id, "rvic", "prm", grid_id, date, "nc"])

    elif dir_name == "hist":
        stop_date = config["OPTIONS"]["STOP_DATE"]
        end_date = str(
            datetime.strptime(stop_date, "%Y-%m-%d").date() + timedelta(days=1)
        )
        filename = ".".join([case_id, "rvic", "h0a", end_date, "nc"])

    outdir = os.path.join(case_dir, dir_name)
    (out_file,) = collect_output_files(filename, outdir)

    return os.path.join(outdir, out_file)


def url_handler(workdir, url):
    if is_opendap_url(url):
        # OPeNDAP
        return url
    elif urlparse(url).scheme and urlparse(url).netloc:
        # HTTP or other
        local_file = os.path.join(workdir, url.split("/")[-1])
        urlretrieve(url, local_file)
        return local_file


def collect_args(request, workdir):
    args = {}
    for k in request.inputs.keys():
        if "data_type" in vars(request.inputs[k][0]).keys():
            # LiteralData
            args[request.inputs[k][0].identifier] = request.inputs[k][0].data
        elif vars(request.inputs[k][0])["_url"] != None:
            args[request.inputs[k][0].identifier] = url_handler(
                workdir, request.inputs[k][0].url
            )
        elif os.path.isfile(request.inputs[k][0].file):
            # Local files
            args[request.inputs[k][0].identifier] = request.inputs[k][0].file

    return args


def params_config_handler(
    workdir, case_id, domain, grid_id, pour_points, routing, uh_box, args
):
    if "params_config_file" in args:
        unprocessed = read_config(args["params_config_file"])
    elif "params_config_dict" in args:
        unprocessed = eval(args["params_config_dict"])
    else:
        unprocessed = params_config_template

    processed = params_config_template

    try:
        processed["OPTIONS"]["CASEID"] = case_id
        processed["OPTIONS"]["GRIDID"] = grid_id

        for upper_key in unprocessed.keys():
            for lower_key in unprocessed[upper_key].keys():
                processed[upper_key][lower_key] = unprocessed[upper_key][lower_key]

        if processed["OPTIONS"]["CASE_DIR"] == None:
            processed["OPTIONS"]["CASE_DIR"] = os.path.join(
                workdir, processed["OPTIONS"]["CASEID"]
            )
        if processed["OPTIONS"]["TEMP_DIR"] == None:
            processed["OPTIONS"]["TEMP_DIR"] = processed["OPTIONS"]["CASEID"] + "/temp"

        processed["POUR_POINTS"]["FILE_NAME"] = pour_points
        processed["UH_BOX"]["FILE_NAME"] = uh_box
        processed["ROUTING"]["FILE_NAME"] = routing
        processed["DOMAIN"]["FILE_NAME"] = domain

        return processed

    except KeyError:
        raise ProcessError("Invalid config key provided")


def convolve_config_handler(
    workdir,
    case_id,
    run_startdate,
    stop_date,
    domain,
    param_file,
    input_forcings,
    args,
):
    if "convolve_config_file" in args:
        unprocessed = read_config(args["convolve_config_file"])
    elif "convolve_config_dict" in args:
        unprocessed = eval(args["convolve_config_dict"])
    else:
        unprocessed = convolve_config_template

    processed = convolve_config_template

    try:
        processed["OPTIONS"]["CASEID"] = case_id
        processed["OPTIONS"]["RUN_STARTDATE"] = run_startdate
        processed["OPTIONS"]["STOP_DATE"] = stop_date

        for upper_key in unprocessed.keys():
            for lower_key in unprocessed[upper_key].keys():
                processed[upper_key][lower_key] = unprocessed[upper_key][lower_key]

        if not processed["OPTIONS"]["CASE_DIR"]:
            processed["OPTIONS"]["CASE_DIR"] = os.path.join(
                workdir, processed["OPTIONS"]["CASEID"]
            )
        if not processed["OPTIONS"]["REST_DATE"]:
            processed["OPTIONS"]["REST_DATE"] = processed["OPTIONS"]["STOP_DATE"]

        processed["DOMAIN"]["FILE_NAME"] = domain
        processed["PARAM_FILE"]["FILE_NAME"] = param_file
        processed["INPUT_FORCINGS"]["DATL_PATH"] = "/".join(
            input_forcings.split("/")[:-1]
        )
        processed["INPUT_FORCINGS"]["DATL_FILE"] = input_forcings.split("/")[-1]

        return processed

    except KeyError:
        raise ProcessError("Invalid config key provided")
