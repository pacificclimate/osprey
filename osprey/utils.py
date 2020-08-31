from pkg_resources import resource_filename
from pywps.app.exceptions import ProcessError
import logging
import os
import json
from datetime import datetime, timedelta
from collections.abc import Iterable
from wps_tools.utils import collect_output_files

logger = logging.getLogger("PYWPS")
logger.setLevel(logging.NOTSET)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: osprey: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def replace_filenames(config, temp_config):
    """
    Replace relative filepaths in config file with
    absolute paths.
    Parameters:
        config (str): Original config file
        temp_config (TemporaryFile): New config file (to be passed into process)
    """
    old_config = open(config, "r")
    filedata = old_config.read()
    old_config.close()

    rel_dir = "tests/data"
    abs_dir = os.path.abspath(resource_filename("tests", "data"))
    newdata = filedata.replace(rel_dir, abs_dir)
    temp_config.writelines(newdata)


def config_hander(workdir, modulue_name, unprocessed, config_template):
    """
    This function enables users to provide dictionary-like string for Configuration input.
    If CASE_DIR and REST_DATE are not provided from a user, their values are derived from
    CASEID and STOP_DATE by default.
    """
    unprocessed = eval(unprocessed)
    try:
        for upper_key in unprocessed.keys():
            for lower_key in unprocessed[upper_key].keys():
                config_template[upper_key][lower_key] = unprocessed[upper_key][
                    lower_key
                ]

        if config_template["OPTIONS"]["CASE_DIR"] == None:
            config_template["OPTIONS"]["CASE_DIR"] = os.path.join(
                workdir, config_template["OPTIONS"]["CASEID"]
            )
        if modulue_name == "convolution":
            if config_template["OPTIONS"]["REST_DATE"] == None:
                config_template["OPTIONS"]["REST_DATE"] = config_template["OPTIONS"][
                    "STOP_DATE"
                ]
        elif modulue_name == "parameters":
            if config_template["OPTIONS"]["TEMP_DIR"] == None:
                config_template["OPTIONS"]["TEMP_DIR"] = (
                    config_template["OPTIONS"]["CASEID"] + "/temp"
                )

        return config_template

    except KeyError as e:
        raise ProcessError("Invalid config key provided")


def get_outfile(config, dir_name):
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
