from .wps_say_hello import SayHello
from .wps_parameters import Parameters

processes = [
    SayHello(),
    Parameters(),
]
