from collections import OrderedDict

params_config_template = OrderedDict(
    {
        # configuration dictionary used for RVIC parameters
        # required user inputs are defined as None value
        "OPTIONS": {
            "LOG_LEVEL": "INFO",
            "VERBOSE": True,
            "CLEAN": False,
            "CASEID": None,
            "GRIDID": None,
            "CASE_DIR": None,
            "TEMP_DIR": None,
            "REMAP": False,
            "AGGREGATE": False,
            "AGG_PAD": 25,
            "NETCDF_FORMAT": "NETCDF4",
            "NETCDF_ZLIB": False,
            "NETCDF_COMPLEVEL": 4,
            "NETCDF_SIGFIGS": None,
            "SUBSET_DAYS": None,
            "CONSTRAIN_FRACTIONS": False,
            "SEARCH_FOR_CHANNEL": False,
        },
        "POUR_POINTS": {"FILE_NAME": None,},
        "UH_BOX": {"FILE_NAME": None, "HEADER_LINES": 1,},
        "ROUTING": {
            "FILE_NAME": None,
            "LONGITUDE_VAR": "lon",
            "LATITUDE_VAR": "lat",
            "FLOW_DISTANCE_VAR": "Flow_Distance",
            "FLOW_DIRECTION_VAR": "Flow_Direction",
            "BASIN_ID_VAR": "Basin_ID",
            "VELOCITY": "velocity",
            "DIFFUSION": "diffusion",
            "VELOCITY": 1,
            "DIFFUSION": 2000,
            "OUTPUT_INTERVAL": 86400,
            "BASIN_FLOWDAYS": 100,
            "CELL_FLOWDAYS": 4,
        },
        "DOMAIN": {
            "FILE_NAME": None,
            "LONGITUDE_VAR": "lon",
            "LATITUDE_VAR": "lat",
            "LAND_MASK_VAR": "mask",
            "FRACTION_VAR": "frac",
            "AREA_VAR": "area",
        },
    }
)

convolve_config_template = OrderedDict(
    {
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
)
