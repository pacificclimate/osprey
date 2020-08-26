from .wps_convolution import Convolution
from .wps_parameters import Parameters
from .wps_full_rvic import FullRVIC

processes = [
    Convolution(),
    Parameters(),
    FullRVIC(),
]
