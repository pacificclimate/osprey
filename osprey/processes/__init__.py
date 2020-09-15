from .wps_convert import Convert
from .wps_convolution import Convolution
from .wps_parameters import Parameters
from .wps_full_rvic import FullRVIC

processes = [
    Convert(),
    Convolution(),
    Parameters(),
    FullRVIC(),
]
