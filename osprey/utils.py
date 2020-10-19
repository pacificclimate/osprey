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


def collect_args(request, workdir):
    args = {}
    for k in request.inputs.keys():
        if "data_type" in vars(request.inputs[k][0]).keys():
            # LiteralData
            args[request.inputs[k][0].identifier] = request.inputs[k][0].data
        elif vars(request.inputs[k][0])["_url"] != None:
            url = request.inputs[k][0].url
            if is_opendap_url(request.inputs[k][0].url):
                # OPeNDAP
                args[request.inputs[k][0].identifier] = url
            elif urlparse(url).scheme and urlparse(url).netloc:
                # HTTP or other
                local_file = os.path.join(workdir, url.split("/")[-1])
                urlretrieve(url, local_file)
                args[request.inputs[k][0].identifier] = local_file
        elif os.path.isfile(request.inputs[k][0].file):
            # Local files
            args[request.inputs[k][0].identifier] = request.inputs[k][0].file

    return args
