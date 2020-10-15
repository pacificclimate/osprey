from pkg_resources import resource_filename
from pywps.app.exceptions import ProcessError
import logging
import os
import requests
from datetime import datetime, timedelta
from collections.abc import Iterable
from wps_tools.utils import collect_output_files
from tempfile import NamedTemporaryFile

logger = logging.getLogger("PYWPS")
logger.setLevel(logging.NOTSET)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: osprey: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def replace_urls(config_file, outdir):
    """
    Copy https URLs to local storage and replace URLs
    with local paths in config file.
    Parameters:
        config_file (str): Config file
        outdir (str): Output directory
    """
    with open(config_file, "r") as read_config:
        filedata = read_config.readlines()

    for i in range(len(filedata)):
        if "https" in filedata[i]:
            url = filedata[i].split(" ")[-1]  # https url is last word in line
            url = url.rstrip()  # remove \n character at end
            r = requests.get(url)
            filename = url.split("/")[-1]
            prefix, suffix = filename.split(".")
            suffix = "." + suffix
            local_file = NamedTemporaryFile(
                suffix=suffix, prefix=prefix, dir=outdir, delete=False
            )
            local_file.write(r.content)
            filedata[i] = filedata[i].replace(url, local_file.name)

    config_filename = config_file.split("/")[-1]
    tmp_config_file = os.path.join(outdir, config_filename)
    with open(tmp_config_file, "w") as write_config:
        for line in filedata:
            write_config.write(f"{line}")

    return tmp_config_file


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


def collect_args(request):
    args = {}
    for k in request.inputs.keys():
        if vars(request.inputs[k][0])["_file"] != None:
            args[request.inputs[k][0].identifier] = request.inputs[k][0].file
        elif vars(request.inputs[k][0])["_url"] != None:
            args[request.inputs[k][0].identifier] = request.inputs[k][0].url
        else:
            args[request.inputs[k][0].identifier] = request.inputs[k][0].data

    return args
