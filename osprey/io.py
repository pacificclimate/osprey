from pywps import LiteralInput, ComplexInput, Format, FORMATS


pour_points_csv = ComplexInput(
    "pour_points_csv",
    "POUR POINTS",
    abstract="Pour Points File content; A comma separated file of outlets to route to [lons, lats]"
    " Use open(filename).read() for local files and a URL for remote files.",
    min_occurs=1,
    max_occurs=1,
    supported_formats=[FORMATS.TEXT, Format("text/csv", extension=".csv")],
)

uh_box_csv = ComplexInput(
    "uh_box_csv",
    "UH BOX",
    abstract="UH Box File content. Use open(filename).read() for local files and a URL for remote files."
    " This defines the unit hydrograph to rout flow to the edge of each grid cell.",
    min_occurs=1,
    max_occurs=1,
    supported_formats=[FORMATS.TEXT, Format("text/csv", extension=".csv")],
)

domain = ComplexInput(
    "domain",
    "Domain",
    abstract="Path to CESM complaint domain file",
    min_occurs=1,
    max_occurs=1,
    supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
)

case_id = LiteralInput(
    "case_id",
    "Case ID",
    abstract="Case ID for the RVIC process",
    min_occurs=1,
    max_occurs=1,
    data_type="string",
)

input_forcings = ComplexInput(
    "input_forcings",
    "Input Forcings",
    abstract="Path to land data netCDF forcings",
    min_occurs=1,
    max_occurs=1,
    supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
)

run_startdate = LiteralInput(
    "run_startdate",
    "Run Start Date",
    abstract="Run start date (yyyy-mm-dd-hh). Only used for startup and drystart runs.",
    min_occurs=1,
    max_occurs=1,
    data_type="string",
)

stop_date = LiteralInput(
    "stop_date",
    "Stop Date",
    abstract="Run stop date based on STOP_OPTION",
    min_occurs=1,
    max_occurs=1,
    data_type="string",
)

convolve_config_file = ComplexInput(
    "convolve_config_file",
    "Convolution Configuration File",
    abstract="Path to input configuration file for Convolution process",
    min_occurs=0,
    max_occurs=1,
    supported_formats=[Format("text/cfg", extension=".cfg")],
)

convolve_config_dict = LiteralInput(
    "convolve_config_dict",
    "Convolution Configuration Dictionary",
    abstract="Dictionary containing input configuration for Convolution process",
    min_occurs=0,
    max_occurs=1,
    data_type="string",
)

version = LiteralInput(
    "version",
    "Version",
    default=True,
    abstract="Return RVIC version string",
    data_type="boolean",
)

np = LiteralInput(
    "np",
    "numofproc",
    default=1,
    abstract="Number of processors used to run job",
    data_type="integer",
)

grid_id = LiteralInput(
    "grid_id",
    "GRID ID",
    abstract="Routing domain grid shortname",
    min_occurs=1,
    max_occurs=1,
    data_type="string",
)

routing = ComplexInput(
    "routing",
    "ROUTING",
    abstract="Path to routing inputs netCDF.",
    min_occurs=1,
    max_occurs=1,
    supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
)

params_config_file = ComplexInput(
    "params_config_file",
    "Parameters Configuration",
    abstract="Path to input configuration file for Parameters process",
    min_occurs=0,
    max_occurs=1,
    supported_formats=[Format("text/cfg", extension=".cfg")],
)
params_config_dict = LiteralInput(
    "params_config_dict",
    "Parameters Configuration Dictionary",
    abstract="Dictionary containing input configuration for Parameters process",
    min_occurs=0,
    max_occurs=1,
    data_type="string",
)
