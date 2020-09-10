#!venv/bin/python3
from rvic import parameters
from rvic.core import share
import re

params_source_file = parameters.__file__
share_source_file = share.__file__

with open(params_source_file, "rt") as params_f:
    params_content = re.sub("\.ix", ".loc", params_f.read())

with open(params_source_file, "wt") as params_f:
    params_f.write(params_content)

with open(share_source_file, "rt") as share_f:
    share_content = re.sub("valid_range", "range", share_f.read())

with open(share_source_file, "wt") as share_f:
    share_f.write(share_content)
