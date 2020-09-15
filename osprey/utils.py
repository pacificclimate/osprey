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


def replace_filenames(config, temp_config):
    """
    Replace relative filepaths in config file with
    absolute paths.
    Parameters:
        config (str): Original config file
        temp_config (TemporaryFile): New config file (to be passed into process)
    """
    with open(config, "r") as old_config:
        filedata = old_config.read()

    rel_dir = "tests/data"
    abs_dir = os.path.abspath(resource_filename("tests", "data"))
    newdata = filedata.replace(rel_dir, abs_dir)
    temp_config.writelines(newdata)


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
