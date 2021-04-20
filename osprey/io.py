from pywps import ComplexInput, Format, FORMATS


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
