from wps_tools.testing import client_for
from pywps import Service


def process_err_test(process, params):
    client = client_for(Service(processes=[process]))
    # exception_el.text only shows the ProcessError message if loglevel is set to DEBUG
    if "loglevel=DEBUG" not in params:
        params += "loglevel=DEBUG"
    resp = client.get(
        service="wps",
        request="Execute",
        version="1.0.0",
        identifier=process.identifier,
        datainputs=params,
    )

    exception_el = resp.xpath(
        "/wps:ExecuteResponse/wps:Status/wps:ProcessFailed/"
        "wps:ExceptionReport/ows:Exception/ows:ExceptionText"
    )

    for elem in exception_el:
        if "Process error" in elem.text:
            return True
    return False
