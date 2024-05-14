from pywps.app.exceptions import ProcessError
import logging
import os
from urllib.parse import urlparse
from urllib.request import urlretrieve
from datetime import datetime, timedelta
from collections import OrderedDict

from wps_tools.file_handling import collect_output_files, is_opendap_url
from wps_tools.io import collect_args
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


def optional_args_handler(args, identifier):
    """
    The function takes an OrderedDict of arguments and rearranges the optional arguments in the right order.
    """
    if identifier + "_config_file" in args.keys():
        config_file = args.pop(identifier + "_config_file")
        args[identifier + "_config_file"] = config_file
    else:
        args[identifier + "_config_file"] = None

    if identifier + "_config_dict" in args.keys():
        config_file = args.pop(identifier + "_config_dict")
        args[identifier + "_config_dict"] = config_file
    else:
        args[identifier + "_config_dict"] = None

    return args


def collect_args_wrapper(request, workdir, modules=[]):
    args = collect_args(request.inputs, workdir)

    if "parameters" in modules:
        optional_args_handler(args, "params")
    if "convolution" in modules:
        optional_args_handler(args, "convolve")

    return [arg if arg != None else arg for arg in args.values()]


def params_config_handler(
    workdir,
    case_id,
    domain,
    grid_id,
    pour_points,
    routing,
    uh_box,
    params_config_file,
    params_config_dict,
):
    if params_config_file:
        unprocessed = read_config(params_config_file)
    elif params_config_dict:
        unprocessed = eval(params_config_dict)
    else:
        unprocessed = params_config_template

    processed = params_config_template

    try:
        processed["OPTIONS"]["CASEID"] = case_id
        processed["OPTIONS"]["GRIDID"] = grid_id

        for section in unprocessed.keys():
            for key in unprocessed[section].keys():
                processed[section][key] = unprocessed[section][key]

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

        return rvic_config_validator(processed)

    except KeyError:
        raise ProcessError("Invalid config key provided in param file")


def convolve_config_handler(
    workdir,
    case_id,
    run_startdate,
    stop_date,
    domain,
    param_file,
    input_forcings,
    convolve_config_file,
    convolve_config_dict,
    listener_port,
):
    if convolve_config_file:
        unprocessed = read_config(convolve_config_file)
    elif convolve_config_dict:
        unprocessed = eval(convolve_config_dict)
    else:
        unprocessed = convolve_config_template

    processed = convolve_config_template

    try:
        processed["OPTIONS"]["LISTENER_PORT"] = listener_port
        processed["OPTIONS"]["CASEID"] = case_id
        processed["OPTIONS"]["RUN_STARTDATE"] = run_startdate
        processed["OPTIONS"]["STOP_DATE"] = stop_date

        for section in unprocessed.keys():
            for key in unprocessed[section].keys():
                processed[section][key] = unprocessed[section][key]

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

        return rvic_config_validator(processed)

    except KeyError:
        raise ProcessError("Invalid config key provided in convolve file ")


def rvic_config_validator(cfg):
    return {
        section: {
            key: cfg[section][key]
            if type(cfg[section][key]) != list or len(cfg[section][key]) > 1
            else cfg[section][key][0]
            for key in cfg[section].keys()
        }
        for section in cfg.keys()
    }


def prep_csv(csv):
    csv.seek(0)
    csv_content = csv.read()

    try:
        csv_content = csv_content.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        pass

    return csv_content
