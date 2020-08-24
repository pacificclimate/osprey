from pkg_resources import resource_filename
from pywps.app.exceptions import ProcessError
import logging
import os
import json
import requests
from datetime import datetime, timedelta
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
    old_config = open(config, "r")
    filedata = old_config.read()
    old_config.close()

    rel_dir = "tests/data"
    abs_dir = os.path.abspath(resource_filename("tests", "data"))
    newdata = filedata.replace(rel_dir, abs_dir)
    temp_config.writelines(newdata)


def replace_urls(config, outdir):
    """
    Copy https URLs to local storage and replace URLs
    with local paths in config file.
    Parameters:
        config (str): Config file
        outdir (str): Output directory
    """
    read_config = open(config, "r")
    filedata = read_config.readlines()
    read_config.close()

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

    write_config = open(config, "w")
    for line in filedata:
        write_config.write(f"{line}")
    write_config.close()


def config_hander(workdir, unprocessed, config_template):
    """
    This function enables users to provide dictionary-like string for Configuration input.
    If CASE_DIR and REST_DATE are not provided from a user, their values are derived from
    CASEID and STOP_DATE by default.
    """
    unprocessed = json.loads(unprocessed)
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
        if config_template["OPTIONS"]["REST_DATE"] == None:
            config_template["OPTIONS"]["REST_DATE"] = config_template["OPTIONS"][
                "STOP_DATE"
            ]

        return config_template

    except KeyError as e:
        raise ProcessError("Invalid config key provided")


def config_file_builder(workdir, config, config_template):
    """
    This function is used for RVIC1.1.0.post1 only since the version requires Configuration input
    to be a .cfg filepath. The function uses information from config to create the file.
    """
    cfg_filepath = os.path.join(workdir, "convolve_file.cfg")
    with open(cfg_filepath, "w") as cfg_file:
        for upper_key in config_template.keys():
            cfg_file.write(f"[{upper_key}]\n")
            for k, v in config_template[upper_key].items():
                cfg_file.write(f"{k}: {str(v)}\n")

    return cfg_filepath


def build_output(config):
    case_id = config["OPTIONS"]["CASEID"]
    stop_date = config["OPTIONS"]["STOP_DATE"]
    end_date = str(datetime.strptime(stop_date, "%Y-%m-%d").date() + timedelta(days=1))

    directory = os.path.join(config["OPTIONS"]["CASE_DIR"], "hist")
    filename = ".".join([case_id, "rvic", "h0a", end_date, "nc"])
    return os.path.join(directory, filename)


def run_rvic(rvic_module, version, config, config_file):
    if version == "1.1.0-1":  # RVIC1.1.0.post1
        cfg_filepath = config_file
        rvic_module(cfg_filepath)
    elif version == "1.1.1":  # RVIC1.1.1
        rvic_module(config)
